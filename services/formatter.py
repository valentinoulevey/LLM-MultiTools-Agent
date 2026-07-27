"""Fonctions de mise en forme et de traduction des données brutes."""
from __future__ import annotations

# Codes météo WMO -> description française (utilisés par Open-Meteo).
WMO_CODES: dict[int, str] = {
    0: "ciel dégagé",
    1: "principalement dégagé",
    2: "partiellement nuageux",
    3: "couvert",
    45: "brouillard",
    48: "brouillard givrant",
    51: "bruine légère",
    53: "bruine modérée",
    55: "bruine dense",
    61: "pluie légère",
    63: "pluie modérée",
    65: "pluie forte",
    71: "neige légère",
    73: "neige modérée",
    75: "neige forte",
    80: "averses légères",
    81: "averses modérées",
    82: "averses violentes",
    95: "orage",
    96: "orage avec grêle",
    99: "orage violent avec grêle",
}


def describe_weather_code(code: int | None) -> str:
    """Traduit un code WMO en description lisible."""
    if code is None:
        return "conditions inconnues"
    return WMO_CODES.get(int(code), f"code météo {code}")


def format_weather(city: str, daily: dict, day_index: int = 1) -> str:
    """Met en forme les prévisions d'un jour donné (0 = aujourd'hui, 1 = demain)."""
    try:
        tmin = daily["temperature_2m_min"][day_index]
        tmax = daily["temperature_2m_max"][day_index]
        rain = daily["precipitation_probability_max"][day_index]
        code = daily["weathercode"][day_index]
    except (KeyError, IndexError):
        return f"Données météo indisponibles pour {city}."

    condition = describe_weather_code(code)
    quand = "demain" if day_index == 1 else "aujourd'hui"
    return (
        f"Météo à {city} ({quand}) : {condition}, "
        f"température {tmin}°C – {tmax}°C, "
        f"probabilité de pluie {rain}%."
    )


def format_pois(location: str, pois: list[dict]) -> str:
    """Met en forme une liste de points d'intérêt."""
    if not pois:
        return f"Aucune activité trouvée autour de « {location} »."
    lignes = [f"{i + 1}. {p['name']}" for i, p in enumerate(pois)]
    return f"Activités trouvées autour de « {location} » :\n" + "\n".join(lignes)
