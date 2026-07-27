"""Outil 3 : recherche d'activités / points d'intérêt."""
from __future__ import annotations

import logging

from langchain_core.tools import tool

from services.api_clients import fetch_pois, geocode
from services.formatter import format_pois

logger = logging.getLogger(__name__)


@tool
def search_activity(location: str, activity_type: str = "culturel") -> str:
    """Recherche des activités (musées, parcs, restaurants...) autour d'un lieu.

    À utiliser quand l'utilisateur cherche quoi faire / visiter dans un quartier.

    Args:
        location: Lieu ou quartier (ex. « le Marais, Paris », « autour du Louvre »).
        activity_type: Type d'activité : musée, culturel, parc, restaurant,
            bar, café, cinéma, monument, attraction.
    """
    point = geocode(location)
    if point is None:
        return f"Lieu introuvable : « {location} »."
    try:
        pois = fetch_pois(point.latitude, point.longitude, activity_type)
    except Exception as exc:
        logger.exception("Erreur recherche d'activités")
        return f"Recherche d'activités impossible ({exc})."
    return format_pois(f"{location} ({activity_type})", pois)
