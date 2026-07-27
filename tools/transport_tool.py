"""Outil 4 : calcul d'itinéraire de transport."""
from __future__ import annotations

import logging

from langchain_core.tools import tool

from services.api_clients import fetch_route, geocode

logger = logging.getLogger(__name__)

# Hypothèses pour l'estimation métro.
METRO_AVG_SPEED_KMH = 25.0
METRO_WAIT_MIN = 5.0


def _estimate_metro(distance_km: float) -> float:
    """Estime la durée en métro : trajet + temps d'attente."""
    travel_min = (distance_km / METRO_AVG_SPEED_KMH) * 60
    return round(travel_min + METRO_WAIT_MIN, 1)


@tool
def get_transport_route(start: str, end: str) -> str:
    """Calcule la distance et la durée d'un trajet entre deux lieux (voiture + métro).

    À utiliser pour estimer un déplacement entre deux points d'une ville.

    Args:
        start: Lieu de départ.
        end: Lieu d'arrivée.
    """
    p_start = geocode(start)
    p_end = geocode(end)
    if p_start is None or p_end is None:
        manquant = start if p_start is None else end
        return f"Lieu introuvable : « {manquant} »."

    try:
        route = fetch_route(p_start, p_end, profile="driving")
    except Exception as exc:
        logger.exception("Erreur calcul d'itinéraire")
        return f"Calcul d'itinéraire impossible ({exc})."

    metro_min = _estimate_metro(route["distance_km"])
    return (
        f"Trajet {start} → {end} :\n"
        f"- Distance : {route['distance_km']} km\n"
        f"- Voiture : ~{route['duration_min']} min\n"
        f"- Métro (estimation) : ~{metro_min} min"
    )
