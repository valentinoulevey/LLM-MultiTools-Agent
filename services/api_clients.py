"""Clients HTTP pour les APIs externes.

APIs utilisées :
- Open-Meteo Geocoding  : ville -> coordonnées GPS
- Nominatim (OSM)       : géocodage de secours (fallback)
- Open-Meteo Forecast   : prévisions météo journalières
- Overpass (OSM)        : recherche de points d'intérêt (activités)
- OSRM                  : calcul d'itinéraire (distance / durée)

Cette couche est la SEULE à effectuer des appels réseau, ce qui rend le reste
du projet facilement testable (on ne mocke qu'un seul module).
"""
from __future__ import annotations

import logging
from dataclasses import dataclass

import requests

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 15  # secondes
# Nominatim et OSRM exigent un User-Agent identifiable.
USER_AGENT = "LLM-MultiTools-Travel-Agent/1.0 (educational project)"

OPEN_METEO_GEOCODING = "https://geocoding-api.open-meteo.com/v1/search"
OPEN_METEO_FORECAST = "https://api.open-meteo.com/v1/forecast"
NOMINATIM_SEARCH = "https://nominatim.openstreetmap.org/search"
OVERPASS_URL = "https://overpass-api.de/api/interpreter"
OSRM_URL = "https://router.project-osrm.org/route/v1"

# Correspondance catégorie utilisateur -> filtre de tags OpenStreetMap.
CATEGORY_TAGS: dict[str, str] = {
    "musée": 'tourism=museum',
    "museum": 'tourism=museum',
    "culturel": 'tourism=museum',
    "culture": 'tourism=museum',
    "parc": 'leisure=park',
    "park": 'leisure=park',
    "restaurant": 'amenity=restaurant',
    "bar": 'amenity=bar',
    "café": 'amenity=cafe',
    "cafe": 'amenity=cafe',
    "cinéma": 'amenity=cinema',
    "cinema": 'amenity=cinema',
    "monument": 'historic=monument',
    "attraction": 'tourism=attraction',
}
DEFAULT_TAG = 'tourism=attraction'


@dataclass
class GeoPoint:
    """Point géographique nommé."""

    name: str
    latitude: float
    longitude: float
    country: str | None = None


# --------------------------------------------------------------------------- #
#  Géocodage
# --------------------------------------------------------------------------- #
def geocode_open_meteo(city: str) -> GeoPoint | None:
    """Géocode une ville via l'API Open-Meteo Geocoding."""
    params = {"name": city, "count": 1, "language": "fr", "format": "json"}
    resp = requests.get(OPEN_METEO_GEOCODING, params=params, timeout=DEFAULT_TIMEOUT)
    resp.raise_for_status()
    results = resp.json().get("results")
    if not results:
        return None
    top = results[0]
    return GeoPoint(
        name=top.get("name", city),
        latitude=float(top["latitude"]),
        longitude=float(top["longitude"]),
        country=top.get("country"),
    )


def geocode_nominatim(query: str) -> GeoPoint | None:
    """Géocode une requête libre via Nominatim (fallback)."""
    params = {"q": query, "format": "json", "limit": 1}
    headers = {"User-Agent": USER_AGENT}
    resp = requests.get(
        NOMINATIM_SEARCH, params=params, headers=headers, timeout=DEFAULT_TIMEOUT
    )
    resp.raise_for_status()
    data = resp.json()
    if not data:
        return None
    item = data[0]
    return GeoPoint(
        name=item.get("display_name", query),
        latitude=float(item["lat"]),
        longitude=float(item["lon"]),
    )


def geocode(location: str) -> GeoPoint | None:
    """Géocode un lieu avec fallback Open-Meteo -> Nominatim.

    Args:
        location: Nom de ville ou de lieu.

    Returns:
        Un ``GeoPoint`` ou ``None`` si introuvable.
    """
    try:
        point = geocode_open_meteo(location)
        if point:
            return point
        logger.info("Open-Meteo n'a rien trouvé pour '%s', fallback Nominatim", location)
    except requests.RequestException as exc:
        logger.warning("Erreur Open-Meteo geocoding (%s), fallback Nominatim", exc)

    try:
        return geocode_nominatim(location)
    except requests.RequestException as exc:
        logger.error("Echec du géocodage Nominatim pour '%s' : %s", location, exc)
        return None


# --------------------------------------------------------------------------- #
#  Météo
# --------------------------------------------------------------------------- #
def fetch_forecast(latitude: float, longitude: float, days: int = 2) -> dict:
    """Récupère les prévisions journalières Open-Meteo.

    Returns:
        Le bloc ``daily`` renvoyé par l'API (listes indexées par jour).
    """
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": (
            "temperature_2m_max,temperature_2m_min,"
            "precipitation_probability_max,weathercode"
        ),
        "timezone": "auto",
        "forecast_days": days,
    }
    resp = requests.get(OPEN_METEO_FORECAST, params=params, timeout=DEFAULT_TIMEOUT)
    resp.raise_for_status()
    return resp.json().get("daily", {})


# --------------------------------------------------------------------------- #
#  Activités (Overpass)
# --------------------------------------------------------------------------- #
def fetch_pois(
    latitude: float,
    longitude: float,
    category: str,
    radius: int = 1500,
    limit: int = 8,
) -> list[dict]:
    """Recherche des points d'intérêt via l'API Overpass (OSM).

    Args:
        latitude, longitude: Centre de la recherche.
        category: Catégorie utilisateur (ex. « musée », « parc »).
        radius: Rayon de recherche en mètres.
        limit: Nombre maximum de résultats.

    Returns:
        Liste de dicts ``{name, category, latitude, longitude}``.
    """
    tag = CATEGORY_TAGS.get(category.lower().strip(), DEFAULT_TAG)
    query = (
        f"[out:json][timeout:25];"
        f"(node[{tag}](around:{radius},{latitude},{longitude});"
        f"way[{tag}](around:{radius},{latitude},{longitude}););"
        f"out center {limit};"
    )
    resp = requests.post(
        OVERPASS_URL,
        data={"data": query},
        headers={"User-Agent": USER_AGENT},
        timeout=30,
    )
    resp.raise_for_status()
    elements = resp.json().get("elements", [])

    pois: list[dict] = []
    for el in elements:
        tags = el.get("tags", {})
        name = tags.get("name")
        if not name:
            continue  # on ignore les lieux sans nom
        lat = el.get("lat") or el.get("center", {}).get("lat")
        lon = el.get("lon") or el.get("center", {}).get("lon")
        pois.append(
            {
                "name": name,
                "category": tag,
                "latitude": lat,
                "longitude": lon,
            }
        )
        if len(pois) >= limit:
            break
    return pois


# --------------------------------------------------------------------------- #
#  Transport (OSRM)
# --------------------------------------------------------------------------- #
def fetch_route(start: GeoPoint, end: GeoPoint, profile: str = "driving") -> dict:
    """Calcule un itinéraire entre deux points via OSRM.

    Args:
        start, end: Points de départ et d'arrivée.
        profile: Profil OSRM (``driving``, ``walking``, ``cycling``).

    Returns:
        Dict ``{distance_km, duration_min}``.
    """
    coords = f"{start.longitude},{start.latitude};{end.longitude},{end.latitude}"
    url = f"{OSRM_URL}/{profile}/{coords}"
    resp = requests.get(
        url,
        params={"overview": "false"},
        headers={"User-Agent": USER_AGENT},
        timeout=DEFAULT_TIMEOUT,
    )
    resp.raise_for_status()
    routes = resp.json().get("routes", [])
    if not routes:
        raise ValueError("Aucun itinéraire trouvé par OSRM.")
    route = routes[0]
    return {
        "distance_km": round(route["distance"] / 1000, 2),
        "duration_min": round(route["duration"] / 60, 1),
    }
