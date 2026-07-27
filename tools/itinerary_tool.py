"""Outil 6 : construction d'un itinéraire complet.

Cet outil ORCHESTRE les autres briques (météo + activités + budget) pour produire
un programme de sortie cohérent. Il appelle directement la couche services afin de
composer un résultat unique et riche en une seule observation pour le LLM.
"""
from __future__ import annotations

import logging

from langchain_core.tools import tool

from services.api_clients import fetch_forecast, fetch_pois, geocode
from services.formatter import format_weather
from tools.budget_tool import AVG_ACTIVITY_COST, AVG_MEAL_COST, AVG_TRANSPORT_COST

logger = logging.getLogger(__name__)


@tool
def build_simple_itinerary(
    location: str,
    num_people: int = 1,
    budget_per_person: float = 50.0,
    activity_type: str = "culturel",
) -> str:
    """Construit un programme de sortie complet (météo + activités + budget).

    À utiliser quand l'utilisateur demande d'ORGANISER une sortie
    (ex. « Organise-moi une sortie à Montmartre pour 4 personnes à 40€/personne »).

    Args:
        location: Lieu de la sortie (ex. « Montmartre, Paris »).
        num_people: Nombre de participants.
        budget_per_person: Budget par personne en euros.
        activity_type: Type d'activités recherchées.
    """
    point = geocode(location)
    if point is None:
        return f"Lieu introuvable : « {location} »."

    # 1) Météo
    try:
        daily = fetch_forecast(point.latitude, point.longitude)
        weather = format_weather(point.name, daily, day_index=1)
    except Exception as exc:
        logger.warning("Météo indisponible pour l'itinéraire : %s", exc)
        weather = "Météo indisponible."

    # 2) Activités
    try:
        pois = fetch_pois(point.latitude, point.longitude, activity_type, limit=4)
        activites = (
            "\n".join(f"  • {p['name']}" for p in pois)
            if pois
            else "  (aucune activité trouvée)"
        )
    except Exception as exc:
        logger.warning("Activités indisponibles : %s", exc)
        activites = "  (recherche d'activités indisponible)"

    # 3) Budget
    fixe = AVG_TRANSPORT_COST * 2 + AVG_MEAL_COST
    reste = budget_per_person - fixe
    nb_activites = max(0, int(reste // AVG_ACTIVITY_COST))
    total = budget_per_person * num_people

    return (
        f"🗺️  Itinéraire proposé pour « {location} » "
        f"({num_people} pers., {budget_per_person:.0f}€/pers.)\n\n"
        f"☀️  {weather}\n\n"
        f"🎭  Activités suggérées ({activity_type}) :\n{activites}\n\n"
        f"💶  Budget : transport A/R ~{AVG_TRANSPORT_COST * 2:.0f}€ + repas "
        f"~{AVG_MEAL_COST:.0f}€ + {nb_activites} activité(s) → "
        f"budget total groupe ~{total:.0f}€."
    )
