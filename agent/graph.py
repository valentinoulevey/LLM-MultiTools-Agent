"""Construction du graphe LangGraph (agent ReAct).

Topologie :

    START -> reasoning --(tool_calls ?)--> tools --> reasoning
                        \\--(sinon)-------> respond -> END

- ``reasoning`` : le LLM (avec outils liés) décide de l'action.
- ``tools``     : exécute les outils demandés et renvoie les observations.
- ``respond``   : extrait la réponse finale en langage naturel.
"""
from __future__ import annotations

import logging

from langchain_core.messages import SystemMessage, ToolMessage
from langgraph.graph import END, START, StateGraph

from agent.prompts import SYSTEM_PROMPT
from agent.router import route_after_reasoning
from agent.state import AgentState
from llm.model import get_llm
from tools import ALL_TOOLS

logger = logging.getLogger(__name__)

_TOOLS_BY_NAME = {tool.name: tool for tool in ALL_TOOLS}


def build_agent(model: str | None = None, checkpointer=None):
    """Compile et retourne l'agent LangGraph.

    Args:
        model: Identifiant du modèle OpenRouter (optionnel).
        checkpointer: Checkpointer LangGraph pour la mémoire (optionnel).

    Returns:
        Un graphe compilé, invocable via ``.invoke`` / ``.stream``.
    """
    llm = get_llm(model)
    llm_with_tools = llm.bind_tools(ALL_TOOLS)

    # --- Noeud 1 : raisonnement (LLM) --------------------------------------
    def reasoning_node(state: AgentState) -> dict:
        """Le LLM analyse l'historique et décide d'appeler des outils ou non."""
        messages = state["messages"]
        # On injecte systématiquement le prompt système en tête.
        if not messages or not isinstance(messages[0], SystemMessage):
            messages = [SystemMessage(content=SYSTEM_PROMPT), *messages]
        response = llm_with_tools.invoke(messages)
        return {"messages": [response]}

    # --- Noeud 2 : exécuteur d'outils --------------------------------------
    def tool_node(state: AgentState) -> dict:
        """Exécute les appels d'outils demandés par le LLM."""
        last_message = state["messages"][-1]
        tool_messages: list[ToolMessage] = []
        used: list[str] = []

        for call in last_message.tool_calls:
            name = call["name"]
            used.append(name)
            tool = _TOOLS_BY_NAME.get(name)
            if tool is None:
                content = f"Outil inconnu : {name}"
                logger.warning(content)
            else:
                try:
                    content = str(tool.invoke(call["args"]))
                except Exception as exc:  # robustesse : jamais de crash du graphe
                    content = f"Erreur lors de l'appel de '{name}' : {exc}"
                    logger.exception("Echec de l'outil %s", name)
            tool_messages.append(
                ToolMessage(content=content, tool_call_id=call["id"], name=name)
            )

        return {"messages": tool_messages, "tools_used": used}

    # --- Noeud 3 : génération de la réponse finale -------------------------
    def respond_node(state: AgentState) -> dict:
        """Extrait la réponse finale produite par le LLM."""
        final = state["messages"][-1].content
        return {"final_answer": final}

    # --- Assemblage du graphe ---------------------------------------------
    graph = StateGraph(AgentState)
    graph.add_node("reasoning", reasoning_node)
    graph.add_node("tools", tool_node)
    graph.add_node("respond", respond_node)

    graph.add_edge(START, "reasoning")
    graph.add_conditional_edges(
        "reasoning",
        route_after_reasoning,
        {"tools": "tools", "respond": "respond"},
    )
    graph.add_edge("tools", "reasoning")  # boucle ReAct
    graph.add_edge("respond", END)

    return graph.compile(checkpointer=checkpointer)
