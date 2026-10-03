"""Local stdio MCP server for deterministic mock weather and pool hours."""

from mcp.server.fastmcp import FastMCP

from mock_data import get_mock_weather, get_public_pool_hours

server = FastMCP("chapter-10-monitoring-mocks")


@server.tool()
def mock_weather(city: str) -> dict[str, object]:
    """Get synthetic weather for Berlin, London, New York, Tokyo, or Sydney."""
    return get_mock_weather(city)


@server.tool()
def public_pool_hours(town: str, weekday: str) -> dict[str, object]:
    """Get synthetic public swimming pool opening hours for a town and weekday."""
    return get_public_pool_hours(town, weekday)


if __name__ == "__main__":
    server.run(transport="stdio")
