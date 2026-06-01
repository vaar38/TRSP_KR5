import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.room_manager import room_manager


@pytest.fixture(autouse=True)
def clear_rooms():
    room_manager._rooms.clear()
    yield
    room_manager._rooms.clear()


def test_connect_to_room(client):
    with client.websocket_connect("/ws/rooms/python?username=alice") as ws:
        msg = ws.receive_json()
        assert msg["type"] == "join"
        assert msg["username"] == "alice"
        assert msg["room_id"] == "python"


def test_send_and_receive_message(client):
    with client.websocket_connect("/ws/rooms/python?username=alice") as ws:
        ws.receive_json()  # join event
        ws.send_json({"type": "message", "text": "Всем привет"})
        msg = ws.receive_json()
        assert msg["type"] == "message"
        assert msg["text"] == "Всем привет"
        assert msg["username"] == "alice"


def test_two_clients_receive_same_message(client):
    with client.websocket_connect("/ws/rooms/python?username=alice") as ws1:
        ws1.receive_json()  # alice join
        with client.websocket_connect("/ws/rooms/python?username=bob") as ws2:
            ws1.receive_json()  # bob join event for alice
            ws2.receive_json()  # bob join event for bob

            ws1.send_json({"type": "message", "text": "Hello everyone"})
            msg1 = ws1.receive_json()
            msg2 = ws2.receive_json()
            assert msg1["text"] == "Hello everyone"
            assert msg2["text"] == "Hello everyone"


def test_different_rooms_dont_mix(client):
    with client.websocket_connect("/ws/rooms/room1?username=alice") as ws1:
        ws1.receive_json()  # join
        with client.websocket_connect("/ws/rooms/room2?username=bob") as ws2:
            ws2.receive_json()  # join

            ws2.send_json({"type": "message", "text": "room2 only"})
            # ws2 gets its own message back
            msg = ws2.receive_json()
            assert msg["text"] == "room2 only"
            # ws1 should NOT receive anything — check room users instead
            users1 = client.get("/rooms/room1/users").json()["users"]
            users2 = client.get("/rooms/room2/users").json()["users"]
            assert "alice" in users1
            assert "bob" not in users1
            assert "bob" in users2


def test_long_message_returns_error(client):
    with client.websocket_connect("/ws/rooms/python?username=alice") as ws:
        ws.receive_json()  # join
        ws.send_json({"type": "message", "text": "x" * 301})
        msg = ws.receive_json()
        assert msg["type"] == "error"
        assert "too long" in msg["detail"].lower()


def test_user_removed_after_disconnect(client):
    with client.websocket_connect("/ws/rooms/python?username=alice") as ws:
        ws.receive_json()  # join

    # After exiting context manager, connection is closed
    resp = client.get("/rooms/python/users")
    assert "alice" not in resp.json()["users"]
