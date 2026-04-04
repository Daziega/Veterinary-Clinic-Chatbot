import pytest
from unittest.mock import patch, MagicMock

from fastapi.testclient import TestClient

from app import app


@pytest.fixture()
def client():
    return TestClient(app)


def test_home_route(client):
    """GET / returns the chat UI page."""
    response = client.get("/")
    assert response.status_code == 200
    assert "ENAE25 Veterinary Clinic" in response.text


def test_chat_empty_message(client):
    """POST /chat with empty message is rejected by Pydantic validation."""
    response = client.post("/chat", json={"message": "", "session_id": "t1"})
    assert response.status_code == 422


def test_chat_missing_body(client):
    """POST /chat with no JSON body is rejected."""
    response = client.post("/chat")
    assert response.status_code == 422


def test_missing_api_key(client):
    """When OPENAI_API_KEY is missing the endpoint returns 500."""
    with patch("app._agent", None):
        with patch("app.build_agent", return_value=None):
            response = client.post(
                "/chat",
                json={"message": "hello", "session_id": "t2"},
            )
            assert response.status_code == 500
            data = response.json()
            assert "OPENAI_API_KEY" in data["detail"]


@patch("app.invoke_agent")
def test_successful_message(mock_invoke, client):
    """Successful agent response is returned in the reply field."""
    mock_invoke.return_value = "Hello, how can I help your pet today?"
    with patch("app._agent", MagicMock()):
        response = client.post(
            "/chat",
            json={"message": "Hi", "session_id": "sess1"},
        )
    assert response.status_code == 200
    data = response.json()
    assert data["reply"] == "Hello, how can I help your pet today?"


@patch("app.invoke_agent")
def test_error_handling(mock_invoke, client):
    """Exceptions are caught and returned as 500 with detail."""
    mock_invoke.side_effect = Exception("OpenAI API timeout")
    with patch("app._agent", MagicMock()):
        response = client.post(
            "/chat",
            json={"message": "Hi", "session_id": "sess2"},
        )
    assert response.status_code == 500
    data = response.json()
    assert "OpenAI API timeout" in data["detail"]


@patch("app.invoke_agent")
def test_default_session_id(mock_invoke, client):
    """Omitting session_id falls back to 'default'."""
    mock_invoke.return_value = "ok"
    with patch("app._agent", MagicMock()):
        response = client.post("/chat", json={"message": "Hi"})
    assert response.status_code == 200
    mock_invoke.assert_called_once()
    _, kwargs_or_args = mock_invoke.call_args
    assert "default" in mock_invoke.call_args.args or "default" in mock_invoke.call_args.kwargs.values()


def test_prompt_loaded_from_file():
    """SYSTEM_PROMPT is loaded from prompt.md and contains key content."""
    from clinic_bot.prompt_loader import SYSTEM_PROMPT
    assert len(SYSTEM_PROMPT) > 100
    assert "sterilisation" in SYSTEM_PROMPT.lower() or "scheduling" in SYSTEM_PROMPT.lower()


def test_config_constants():
    """Config module exports correct business rule values."""
    from clinic_bot.config import MAX_DAILY_MINUTES, MAX_DOGS_PER_DAY, OPERATING_DAYS
    assert MAX_DAILY_MINUTES == 240
    assert MAX_DOGS_PER_DAY == 2
    assert OPERATING_DAYS == [0, 1, 2, 3]
