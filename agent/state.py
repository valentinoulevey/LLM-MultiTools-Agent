"""État partagé du graphe LangGraph.

L'historique de conversation (``messages``) contient à la fois le message
utilisateur, les tours précédents, les appels d'outils et leurs observations :
c'est le coeur de la boucle ReAct.
"""
from __future__ import annotations

import operator
from typing import Annotated, TypedDict

from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """Structure d'état circulant entre les noeuds du graphe.

    Attributes:
        messages: Historique complet (Human / AI / Tool). Le reducer
            ``add_messages`` gère l'ajout et le dédoublonnage.
        tools_used: Noms des outils appelés durant le tour courant,
            accumulés via ``operator.add`` (pour l'affichage UI).
        final_answer: Réponse finale en langage naturel destinée à l'utilisateur.
    """

    messages: Annotated[list[AnyMessage], add_messages]
    tools_used: Annotated[list[str], operator.add]
    final_answer: str
