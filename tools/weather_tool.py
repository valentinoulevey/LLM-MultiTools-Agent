"""Outil 1 : météo d'une ville."""
from __future__ import annotations

import logging

from langchain_core.tools import tool

from services.api_clients import fetch_forecast, geocode
from services.formatter import format_weather

logger = logging.getLogger(__name__)


@tool
def get_weather(city: str) -> str:
    """Donne la météo de DEMAIN pour une ville (température min/max, pluie, conditions).

    À utiliser quand l'utilisateur demande le temps qu'il fera dans une ville.

    Args:
        city: Nom de la ville (ex. « Paris », « Lyon »).
    """
    point = geocode(city)
    if point is None:
        return f"Ville introuvable : « {city} »."
    try:
        daily = fetch_forecast(point.latitude, point.longitude)
    except Exception as exc:  # erreur réseau / API
        logger.exception("Erreur météo")
        return f"Impossible de récupérer la météo de {city} ({exc})."
    return format_weather(point.name, daily, day_index=1)
