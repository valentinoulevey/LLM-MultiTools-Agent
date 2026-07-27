"""Tests de la logique de routage ReAct (sans appel LLM)."""
from langchain_core.messages import AIMessage

from agent.router import route_after_reasoning


def test_route_to_tools_when_tool_calls_present():
    """Un message IA avec appels d'outils route vers 'tools'."""
    ai = AIMessage(
        content="",
        tool_calls=[{"name": "get_weather", "args": {"city": "Paris"}, "id": "1"}],
    )
    state = {"messages": [ai], "tools_used": [], "final_answer": ""}
    assert route_after_reasoning(state) == "tools"


def test_route_to_respond_without_tool_calls():
    """Un message IA sans appel d'outil route vers 'respond'."""
    ai = AIMessage(content="Il fera beau demain.")
    state = {"messages": [ai], "tools_used": [], "final_answer": ""}
    assert route_after_reasoning(state) == "respond"


def test_route_respond_on_empty_history():
    """Un historique vide route par défaut vers 'respond'."""
    state = {"messages": [], "tools_used": [], "final_answer": ""}
    assert route_after_reasoning(state) == "respond"


def test_all_tools_registered():
    """Les 6 outils attendus sont bien exposés à l'agent."""
    from tools import ALL_TOOLS

    names = {t.name for t in ALL_TOOLS}
    assert names == {
        "get_weather",
        "compare_weather",
        "search_activity",
        "get_transport_route",
        "estimate_budget",
        "build_simple_itinerary",
    }
