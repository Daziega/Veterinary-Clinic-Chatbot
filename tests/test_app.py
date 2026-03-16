import pytest
from unittest.mock import patch, MagicMock
from app import app, get_session_history, _store

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_home_route(client):
    """AC1: Navigating to the root URL loads the UI successfully."""
    response = client.get('/')
    assert response.status_code == 200
    assert b"Vet Clinic Chatbot" in response.data

def test_empty_message(client):
    """AC2: Submitting an empty message reliably prompts the user without crashing."""
    response = client.post('/ask_bot', data={'msg': '   ', 'session_id': 'test2'})
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data['msg'] == "Please send a non-empty message."

def test_missing_api_key(client):
    """AC5: Ensure error handling when API key isn't set (before mock injection)."""
    with patch('app.os.environ.get', return_value=None):
        with patch('app._bot_chain', None):
            response = client.post('/ask_bot', data={'msg': 'hello', 'session_id': 'test'})
            assert response.status_code == 500
            json_data = response.get_json()
            assert "OPENAI_API_KEY is not set" in json_data['msg']

@patch('app._bot_chain')
def test_successful_message(mock_chain, client):
    """Check successful LLM response formatting."""
    mock_response = MagicMock()
    mock_response.content = "Hello, how can I help your pet today?"
    mock_chain.invoke.return_value = mock_response

    response = client.post('/ask_bot', data={'msg': 'Hi', 'session_id': 'sess1'})
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['msg'] == "Hello, how can I help your pet today?"
    
    # Ensure session id was passed in config
    mock_chain.invoke.assert_called_once()
    called_config = mock_chain.invoke.call_args[1].get('config')
    assert called_config == {"configurable": {"session_id": "sess1"}}

@patch('app._bot_chain')
def test_error_handling(mock_chain, client):
    """AC5: Exception handling without exposing stack traces."""
    mock_chain.invoke.side_effect = Exception("OpenAI API timeout")
    
    response = client.post('/ask_bot', data={'msg': 'Hi', 'session_id': 'sess1'})
    assert response.status_code == 500
    json_data = response.get_json()
    assert json_data['msg'] == "Error: OpenAI API timeout"

def test_get_session_history():
    """AC4: Check session isolation helper behavior."""
    # Ensure memory store works independently per session_id
    id1 = "browser_a"
    id2 = "browser_b"
    
    hist1 = get_session_history(id1)
    hist2 = get_session_history(id2)
    
    assert hist1 is not hist2
    assert id1 in _store
    assert id2 in _store
    
    # Reset store for cleanup
    _store.clear()
