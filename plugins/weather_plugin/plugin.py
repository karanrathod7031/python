"""Weather plugin — fetch weather data from a free API."""

from __future__ import annotations

from typing import Any

from app.plugins.base import BasePlugin, PluginInfo


class WeatherPlugin(BasePlugin):
    """Plugin to fetch weather information."""

    def get_info(self) -> PluginInfo:
        return PluginInfo(
            name="weather",
            version="1.0.0",
            description="Fetch current weather information for any city",
            author="Jarvis Team",
            commands=["weather", "forecast"],
        )

    def get_commands(self) -> list[str]:
        return ["weather", "forecast"]

    async def execute(self, command: str, args: dict[str, Any]) -> dict[str, Any]:
        city = args.get("city", "London")

        if command == "weather":
            return await self._get_weather(city)
        elif command == "forecast":
            return await self._get_weather(city)

        return {"status": "error", "message": f"Unknown command: {command}"}

    async def _get_weather(self, city: str) -> dict[str, Any]:
        """Fetch weather using wttr.in API (no API key needed)."""
        try:
            import httpx

            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"https://wttr.in/{city}?format=j1"
                )
                response.raise_for_status()
                data = response.json()

            current = data.get("current_condition", [{}])[0]
            return {
                "status": "success",
                "city": city,
                "temperature_c": current.get("temp_C", "N/A"),
                "temperature_f": current.get("temp_F", "N/A"),
                "description": current.get("weatherDesc", [{}])[0].get("value", "N/A"),
                "humidity": current.get("humidity", "N/A"),
                "wind_kmph": current.get("windspeedKmph", "N/A"),
                "feels_like_c": current.get("FeelsLikeC", "N/A"),
            }
        except ImportError:
            return {"status": "error", "message": "httpx not installed"}
        except Exception as exc:
            return {"status": "error", "message": str(exc)}
