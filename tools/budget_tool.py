"""Outil 5 : estimation de budget pour une sortie."""
from __future__ import annotations

from langchain_core.tools import tool

# Hypothèses de coûts moyens (en euros).
AVG_ACTIVITY_COST = 15.0   # coût moyen d'une activité par personne
AVG_TRANSPORT_COST = 4.0   # coût transport par personne (aller simple)
AVG_MEAL_COST = 18.0       # coût moyen d'un repas par personne


@tool
def estimate_budget(num_people: int, total_budget: float) -> str:
    """Estime ce qu'un groupe peut faire avec un budget donné (activités, repas, transport).

    À utiliser quand l'utilisateur mentionne un budget et un nombre de personnes.

    Args:
        num_people: Nombre de personnes.
        total_budget: Budget total disponible en euros.
    """
    if num_people <= 0:
        return "Le nombre de personnes doit être positif."
    if total_budget <= 0:
        return "Le budget doit être positif."

    per_person = total_budget / num_people
    transport = AVG_TRANSPORT_COST * 2  # aller-retour
    meal = AVG_MEAL_COST
    remaining = per_person - transport - meal
    activities = max(0, int(remaining // AVG_ACTIVITY_COST))
    fixed = (transport + meal) * num_people
    activities_cost = activities * AVG_ACTIVITY_COST * num_people
    total_est = fixed + activities_cost

    return (
        f"Estimation budget pour {num_people} personne(s) — "
        f"{total_budget:.0f}€ ({per_person:.0f}€/personne) :\n"
        f"- Transport (A/R) : {transport:.0f}€/personne\n"
        f"- Repas : {meal:.0f}€/personne\n"
        f"- Activités possibles : {activities} par personne "
        f"(~{AVG_ACTIVITY_COST:.0f}€ l'unité)\n"
        f"- Coût total approximatif : {total_est:.0f}€ "
        f"(reste ~{max(0, per_person - transport - meal - activities * AVG_ACTIVITY_COST):.0f}€/personne)"
    )
