"""Tests de l'outil transport (réseau mocké)."""
from services.api_clients import GeoPoint
from tools import transport_tool
from tools.transport_tool import _estimate_metro


def test_metro_estimate_positive():
    """L'estimation métro augmente avec la distance et inclut l'attente."""
    assert _estimate_metro(5) > _estimate_metro(1)
    assert _estimate_metro(0) == transport_tool.METRO_WAIT_MIN


def test_get_transport_route_ok(monkeypatch):
    """Le trajet renvoie distance, durée voiture et estimation métro."""
    monkeypatch.setattr(
        transport_tool,
        "geocode",
        lambda name: GeoPoint(name, 48.85, 2.35),
    )
    monkeypatch.setattr(
        transport_tool,
        "fetch_route",
        lambda s, e, profile="driving": {"distance_km": 5.0, "duration_min": 12.0},
    )
    result = transport_tool.get_transport_route.invoke(
        {"start": "Louvre", "end": "Montmartre"}
    )
    assert "5.0 km" in result
    assert "Métro" in result


def test_get_transport_route_missing_place(monkeypatch):
    """Un lieu introuvable est signalé."""
    monkeypatch.setattr(transport_tool, "geocode", lambda name: None)
    result = transport_tool.get_transport_route.invoke({"start": "X", "end": "Y"})
    assert "introuvable" in result.lower()
