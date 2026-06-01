from fastapi import WebSocket


class RoomManager:
    def __init__(self):
        # room_id -> {username: websocket}
        self._rooms: dict[str, dict[str, WebSocket]] = {}

    async def connect(self, room_id: str, username: str, websocket: WebSocket):
        await websocket.accept()
        if room_id not in self._rooms:
            self._rooms[room_id] = {}
        self._rooms[room_id][username] = websocket
        await self.broadcast(
            room_id,
            {"type": "join", "room_id": room_id, "username": username},
        )

    async def disconnect(self, room_id: str, username: str):
        if room_id in self._rooms:
            self._rooms[room_id].pop(username, None)
            if not self._rooms[room_id]:
                del self._rooms[room_id]

    async def broadcast(self, room_id: str, payload: dict):
        connections = self._rooms.get(room_id, {})
        for ws in list(connections.values()):
            try:
                await ws.send_json(payload)
            except Exception:
                pass

    def get_users(self, room_id: str) -> list[str]:
        return list(self._rooms.get(room_id, {}).keys())


room_manager = RoomManager()
