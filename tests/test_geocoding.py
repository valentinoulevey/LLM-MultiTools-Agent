"""Tests du géocodage et de son mécanisme de fallback."""
import requests

from services import api_clients
from services.api_clients import GeoPoint, geocode


def test_geocode_uses_open_meteo_first(monkeypatch):
    """Si Open-Meteo répond, on ne fait pas de fallback."""
    monkeypatch.setattr(
        api_clients, "geocode_open_meteo", lambda c: GeoPoint("Lyon", 45.75, 4.85)
    )
    monkeypatch.setattr(
        api_clients,
        "geocode_nominatim",
        lambda q: (_ for _ in ()).throw(AssertionError("fallback ne doit pas être appelé")),
    )
    point = geocode("Lyon")
    assert point is not None
    assert point.name == "Lyon"


def test_geocode_fallback_to_nominatim(monkeypatch):
    """Si Open-Meteo échoue, on bascule sur Nominatim."""

    def boom(_city):
        raise requests.RequestException("API down")

    monkeypatch.setattr(api_clients, "geocode_open_meteo", boom)
    monkeypatch.setattr(
        api_clients, "geocode_nominatim", lambda q: GeoPoint("Marais", 48.86, 2.36)
    )
    point = geocode("le Marais")
    assert point is not None
    assert point.name == "Marais"


def test_geocode_returns_none_when_all_fail(monkeypatch):
    """Si tout échoue, on renvoie None sans lever d'exception."""
    monkeypatch.setattr(api_clients, "geocode_open_meteo", lambda c: None)

    def boom(_q):
        raise requests.RequestException("down")

    monkeypatch.setattr(api_clients, "geocode_nominatim", boom)
    assert geocode("Nulle part") is None
