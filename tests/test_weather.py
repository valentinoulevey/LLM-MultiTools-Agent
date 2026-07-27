"""Tests de l'outil météo (réseau mocké)."""
from services.api_clients import GeoPoint
from tools import weather_tool


def test_get_weather_ok(monkeypatch):
    """La météo est formatée correctement à partir de données simulées."""
    monkeypatch.setattr(
        weather_tool, "geocode", lambda city: GeoPoint("Paris", 48.85, 2.35, "France")
    )
    monkeypatch.setattr(
        weather_tool,
        "fetch_forecast",
        lambda lat, lon: {
            "temperature_2m_min": [10, 12],
            "temperature_2m_max": [18, 20],
            "precipitation_probability_max": [10, 30],
            "weathercode": [1, 61],
        },
    )
    result = weather_tool.get_weather.invoke({"city": "Paris"})
    assert "Paris" in result
    assert "20°C" in result
    assert "pluie légère" in result


def test_get_weather_city_not_found(monkeypatch):
    """Une ville introuvable renvoie un message explicite."""
    monkeypatch.setattr(weather_tool, "geocode", lambda city: None)
    result = weather_tool.get_weather.invoke({"city": "Villeinconnue"})
    assert "introuvable" in result.lower()
