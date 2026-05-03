"""WebSocket handler for real-time communication."""

from __future__ import annotations

import json
from typing import Any

from fastapi import WebSocket, WebSocketDisconnect

from app.utils.logger import setup_logger

logger = setup_logger("jarvis.api.websocket")


class ConnectionManager:
    """Manage WebSocket connections."""

    def __init__(self) -> None:
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        """Accept a new WebSocket connection."""
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket) -> None:
        """Remove a WebSocket connection."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total: {len(self.active_connections)}")

    async def send_json(self, websocket: WebSocket, data: dict[str, Any]) -> None:
        """Send JSON data to a specific client."""
        try:
            await websocket.send_json(data)
        except Exception as exc:
            logger.error(f"WebSocket send error: {exc}")
            self.disconnect(websocket)

    async def broadcast(self, data: dict[str, Any]) -> None:
        """Broadcast JSON data to all connected clients."""
        disconnected: list[WebSocket] = []
        for ws in self.active_connections:
            try:
                await ws.send_json(data)
            except Exception:
                disconnected.append(ws)

        for ws in disconnected:
            self.disconnect(ws)


ws_manager = ConnectionManager()


async def websocket_endpoint(websocket: WebSocket) -> None:
    """Handle WebSocket connections for real-time chat."""
    await ws_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
            except json.JSONDecodeError:
                message = {"text": data}

            text = message.get("text", "")
            if not text:
                await ws_manager.send_json(
                    websocket, {"error": "No text provided"}
                )
                continue

            # Process through brain
            from app.main import get_brain

            brain = get_brain()
            result = await brain.process(text)

            await ws_manager.send_json(websocket, result)

    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception as exc:
        logger.error(f"WebSocket error: {exc}")
        ws_manager.disconnect(websocket)
