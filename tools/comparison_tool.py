"""Outil 2 : comparaison météo entre deux villes."""
from __future__ import annotations

import logging

from langchain_core.tools import tool

from services.api_clients import fetch_forecast, geocode
from services.formatter import describe_weather_code

logger = logging.getLogger(__name__)


def _summary(city: str) -> dict | None:
    point = geocode(city)
    if point is None:
        return None
    daily = fetch_forecast(point.latitude, point.longitude)
    try:
        return {
            "name": point.name,
            "tmin": daily["temperature_2m_min"][1],
            "tmax": daily["temperature_2m_max"][1],
            "rain": daily["precipitation_probability_max"][1],
            "condition": describe_weather_code(daily["weathercode"][1]),
        }
    except (KeyError, IndexError):
        return None


@tool
def compare_weather(city1: str, city2: str) -> str:
    """Compare la météo de DEMAIN entre deux villes (température, pluie, conditions).

    À utiliser quand l'utilisateur veut comparer deux villes (« Paris ou Lyon ? »).

    Args:
        city1: Première ville.
        city2: Seconde ville.
    """
    try:
        a = _summary(city1)
        b = _summary(city2)
    except Exception as exc:
        logger.exception("Erreur comparaison météo")
        return f"Comparaison impossible ({exc})."

    if a is None or b is None:
        manquante = city1 if a is None else city2
        return f"Comparaison impossible : données indisponibles pour « {manquante} »."

    plus_chaud = a["name"] if a["tmax"] >= b["tmax"] else b["name"]
    plus_sec = a["name"] if a["rain"] <= b["rain"] else b["name"]

    return (
        f"Comparaison météo (demain) :\n"
        f"- {a['name']} : {a['condition']}, {a['tmin']}–{a['tmax']}°C, pluie {a['rain']}%\n"
        f"- {b['name']} : {b['condition']}, {b['tmin']}–{b['tmax']}°C, pluie {b['rain']}%\n"
        f"➜ Plus chaud : {plus_chaud}. Plus sec : {plus_sec}."
    )
