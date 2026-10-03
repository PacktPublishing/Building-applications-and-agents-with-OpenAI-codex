"""Synthetic fixtures used by the local MCP tools."""

WEATHER = {
    "Berlin": {"condition": "light rain", "temperature_c": 14},
    "London": {"condition": "cloudy", "temperature_c": 16},
    "New York": {"condition": "sunny", "temperature_c": 22},
    "Tokyo": {"condition": "clear", "temperature_c": 25},
    "Sydney": {"condition": "showers", "temperature_c": 18},
}

POOL_HOURS = {
    "Riverton": {
        "Monday": [
            {"pool": "Riverton Central Pool", "opens": "06:00", "closes": "20:00"},
            {"pool": "Riverton Riverside Pool", "opens": "09:00", "closes": "18:00"},
        ],
        "Tuesday": [
            {"pool": "Riverton Central Pool", "opens": "06:00", "closes": "20:00"},
            {"pool": "Riverton Riverside Pool", "opens": "09:00", "closes": "18:00"},
        ],
        "Wednesday": [
            {"pool": "Riverton Central Pool", "opens": "06:00", "closes": "20:00"},
            {"pool": "Riverton Riverside Pool", "opens": "12:00", "closes": "20:00"},
        ],
        "Thursday": [
            {"pool": "Riverton Central Pool", "opens": "06:00", "closes": "20:00"},
            {"pool": "Riverton Riverside Pool", "opens": "09:00", "closes": "18:00"},
        ],
        "Friday": [
            {"pool": "Riverton Central Pool", "opens": "06:00", "closes": "21:00"},
            {"pool": "Riverton Riverside Pool", "opens": "09:00", "closes": "19:00"},
        ],
        "Saturday": [
            {"pool": "Riverton Central Pool", "opens": "08:00", "closes": "20:00"},
            {"pool": "Riverton Riverside Pool", "opens": "10:00", "closes": "18:00"},
        ],
        "Sunday": [
            {"pool": "Riverton Central Pool", "opens": "08:00", "closes": "18:00"},
            {"pool": "Riverton Riverside Pool", "opens": "10:00", "closes": "16:00"},
        ],
    }
}


def get_mock_weather(city: str) -> dict[str, object]:
    """Return synthetic weather for one of the five supported cities."""
    if city not in WEATHER:
        supported = ", ".join(WEATHER)
        raise ValueError(f"Unsupported city {city!r}. Choose one of: {supported}.")
    return {"source": "mock data", "city": city, **WEATHER[city]}


def get_public_pool_hours(town: str, weekday: str) -> dict[str, object]:
    """Return synthetic public pool hours for Riverton on a named weekday."""
    if town not in POOL_HOURS:
        raise ValueError(f"No mock pool schedule is available for {town!r}.")
    schedule = POOL_HOURS[town]
    if weekday not in schedule:
        raise ValueError(f"Invalid weekday {weekday!r}. Use a full English weekday name.")
    return {
        "source": "mock data",
        "town": town,
        "weekday": weekday,
        "pools": schedule[weekday],
    }
