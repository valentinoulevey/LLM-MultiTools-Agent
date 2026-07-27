"""Registre central des outils exposés à l'agent."""
from tools.activity_tool import search_activity
from tools.budget_tool import estimate_budget
from tools.comparison_tool import compare_weather
from tools.itinerary_tool import build_simple_itinerary
from tools.transport_tool import get_transport_route
from tools.weather_tool import get_weather

# Liste liée au LLM via ``bind_tools`` dans le graphe.
ALL_TOOLS = [
    get_weather,
    compare_weather,
    search_activity,
    get_transport_route,
    estimate_budget,
    build_simple_itinerary,
]

__all__ = [
    "ALL_TOOLS",
    "get_weather",
    "compare_weather",
    "search_activity",
    "get_transport_route",
    "estimate_budget",
    "build_simple_itinerary",
]
