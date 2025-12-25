from fastapi import WebSocket
from datetime import datetime, timezone
from fastapi.encoders import jsonable_encoder
from logger import log

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        log("websocket", f"Подключен клиент ({len(self.active_connections)})")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        log("websocket", f"Клиент отключен ({len(self.active_connections)})")

    async def broadcast_json(self, data: dict):
        for ws in self.active_connections:
            try:
                await ws.send_json(data)
            except Exception as e:
                log("error", f"WebSocket send error: {e}")
                self.disconnect(ws)

manager = ConnectionManager()
