"""Logique de routage de la boucle ReAct.

Après le noeud de raisonnement, on regarde le dernier message produit par le LLM :
- s'il contient des appels d'outils -> on route vers le noeud ``tools`` ;
- sinon -> le LLM a produit sa réponse finale, on route vers ``respond``.
"""
from __future__ import annotations

from agent.state import AgentState


def route_after_reasoning(state: AgentState) -> str:
    """Décide de l'étape suivante après le noeud de raisonnement.

    Args:
        state: État courant du graphe.

    Returns:
        ``"tools"`` si le LLM demande l'exécution d'outils, sinon ``"respond"``.
    """
    messages = state["messages"]
    if not messages:
        return "respond"

    last_message = messages[-1]
    tool_calls = getattr(last_message, "tool_calls", None)
    if tool_calls:
        return "tools"
    return "respond"
