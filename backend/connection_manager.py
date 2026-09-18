from fastapi import WebSocket
from typing import Dict, List
import uuid


class ConnectionManager:
    def __init__(self):
        # Maps a trip_id to a list of active WebSocket connections for that trip
        self.active_connections: Dict[uuid.UUID, List[WebSocket]] = {}

    async def connect(self, trip_id: uuid.UUID, websocket: WebSocket):
        await websocket.accept()
        if trip_id not in self.active_connections:
            self.active_connections[trip_id] = []
        self.active_connections[trip_id].append(websocket)

    def disconnect(self, trip_id: uuid.UUID, websocket: WebSocket):
        if trip_id in self.active_connections:
            self.active_connections[trip_id].remove(websocket)
            if not self.active_connections[trip_id]:
                del self.active_connections[trip_id]

    async def broadcast(self, trip_id: uuid.UUID, message: dict, exclude: WebSocket = None):
        if trip_id not in self.active_connections:
            return
        for connection in self.active_connections[trip_id]:
            if connection != exclude:
                await connection.send_json(message)


manager = ConnectionManager()