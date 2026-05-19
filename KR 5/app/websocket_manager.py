from typing import Dict, Set
from fastapi import WebSocket, WebSocketDisconnect


class RoomManager:
    def __init__(self):
        self.rooms: Dict[str, Set[WebSocket]] = {}

    async def connect(self, room_id: str, username: str, websocket: WebSocket):
        await websocket.accept()
        self.rooms.setdefault(room_id, set()).add(websocket)

        await self.broadcast(
            room_id,
            {
                "type": "system",
                "event": "user_joined",
                "room_id": room_id,
                "username": username,
                "users": await self.get_users(room_id),
            },
        )

    def disconnect(self, room_id: str, username: str, websocket: WebSocket):
        conns = self.rooms.get(room_id)
        if conns:
            conns.discard(websocket)
            if not conns:
                self.rooms.pop(room_id, None)

    async def broadcast(self, room_id: str, message: dict):
        for client in list(self.rooms.get(room_id, [])):
            try:
                await client.send_json(message)
            except WebSocketDisconnect:
                pass

    async def send_error(self, websocket: WebSocket, detail: str):
        await websocket.send_json({"type": "error", "detail": detail})

    async def get_users(self, room_id: str) -> list:
        return [f"user_{i}" for i in range(len(self.rooms.get(room_id, [])))]



room_manager = RoomManager()