import pytest
from unittest.mock import patch, MagicMock

from Backend.Connectors.LLM_Connector import LLMConnector


@patch("Backend.Connectors.LLM_Connector.OllamaLLM")
def test_llm_connect_default_args(mock_ollama_llm):
    # Arrange
    mock_instance = MagicMock()
    mock_ollama_llm.return_value = mock_instance

    # Act
    result = LLMConnector.llm_connect()

    # Assert
    mock_ollama_llm.assert_called_once_with(
        model="qwen3:4b",
        base_url="",
        temperature=0
    )
    assert result is mock_instance


@patch("Backend.Connectors.LLM_Connector.OllamaLLM")
def test_llm_connect_custom_args(mock_ollama_llm):
    # Arrange
    mock_instance = MagicMock()
    mock_ollama_llm.return_value = mock_instance

    model = "llama3"
    base_url = "http://localhost:11434"

    # Act
    result = LLMConnector.llm_connect(model=model, base_url=base_url)

    # Assert
    mock_ollama_llm.assert_called_once_with(
        model=model,
        base_url=base_url,
        temperature=0
    )
    assert result is mock_instance


@patch("Backend.Connectors.LLM_Connector.OllamaLLM")
def test_llm_returns_response_for_message(mock_ollama_llm):
    # Arrange
    mock_instance = MagicMock()
    mock_instance.return_value = "Hello! 👋"  # ← correct way
    mock_ollama_llm.return_value = mock_instance

    # Act
    llm = LLMConnector.llm_connect()
    response = llm("hi")

    # Assert
    assert response is not None
    assert isinstance(response, str)
    assert len(response) > 0

    mock_instance.assert_called_once_with("hi")

    mock_instance.invoke.return_value = "Hello!"
    response = llm.invoke("hi")
    mock_instance.invoke.assert_called_once_with("hi")