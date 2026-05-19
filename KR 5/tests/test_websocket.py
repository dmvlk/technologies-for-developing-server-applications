import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_websocket_connect_success(client):
    with client.websocket_connect("/ws/rooms/test?username=alice") as websocket:
        data = websocket.receive_json()
        assert data["type"] == "system"
        assert data["event"] == "user_joined"
        assert data["username"] == "alice"


def test_websocket_connect_missing_username(client):
    with pytest.raises(Exception):
        with client.websocket_connect("/ws/rooms/test") as websocket:
            pass


def test_websocket_send_message(client):
    with client.websocket_connect("/ws/rooms/test?username=bob") as websocket:
        msg = websocket.receive_json()
        assert msg["type"] == "system"

        websocket.send_json({"text": "Hello, world!"})
        response = websocket.receive_json()

        assert response["type"] == "message"
        assert response["username"] == "bob"
        assert response["text"] == "Hello, world!"


def test_websocket_message_too_long(client):
    with client.websocket_connect("/ws/rooms/test?username=charlie") as websocket:
        websocket.receive_json()

        long_message = "x" * 301
        websocket.send_json({"text": long_message})
        error_response = websocket.receive_json()

        assert error_response["type"] == "error"
        assert error_response["detail"] == "Message is too long"


def test_websocket_broadcast_to_room(client):
    with client.websocket_connect("/ws/rooms/chat?username=alice") as ws1:
        msg1 = ws1.receive_json()
        assert msg1["type"] == "system"
        assert msg1["event"] == "user_joined"
        assert msg1["username"] == "alice"

        with client.websocket_connect("/ws/rooms/chat?username=bob") as ws2:

            msg2 = ws2.receive_json()
            assert msg2["type"] == "system"
            assert msg2["event"] == "user_joined"
            assert msg2["username"] == "bob"

            notification = ws1.receive_json()
            assert notification["type"] == "system"
            assert notification["event"] == "user_joined"
            assert notification["username"] == "bob"

            ws1.send_json({"text": "Hi everyone!"})

            response1 = ws1.receive_json()
            response2 = ws2.receive_json()

            assert response1["type"] == "message"
            assert response2["type"] == "message"
            assert response1["text"] == "Hi everyone!"
            assert response2["text"] == "Hi everyone!"
            assert response1["username"] == "alice"
            assert response2["username"] == "alice"


def test_websocket_different_rooms(client):
    with client.websocket_connect("/ws/rooms/room1?username=alice") as ws1, \
            client.websocket_connect("/ws/rooms/room2?username=bob") as ws2:

        ws1.receive_json()
        ws2.receive_json()
        ws1.send_json({"text": "Message in room1"})

        msg1 = ws1.receive_json()
        assert msg1["type"] == "message"
        assert msg1["text"] == "Message in room1"

        with pytest.raises(Exception):
            ws2.receive_json(timeout=0.5)


def test_websocket_disconnect_removes_user(client):
    with client.websocket_connect("/ws/rooms/disco?username=dave") as websocket:
        websocket.receive_json()

        response = client.get("/rooms/disco/users")
        assert response.status_code == 200
        assert "users" in response.json()

    response = client.get("/rooms/disco/users")
    assert response.status_code == 200