"""
Pruebas unitarias para el cliente de Hugging Face.

Ejecutar con:
    pytest test_hf_client.py -v
"""
import os
import sys
from pathlib import Path
import pytest
from unittest.mock import patch, MagicMock

# Asegurar que el directorio raíz del proyecto esté en el PYTHONPATH
PROJECT_ROOT = Path(__file__).parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from hf_client import process_ocr, client

@pytest.fixture
def mock_client():
    """Fixture que proporciona un cliente mock de Hugging Face."""
    with patch('hf_client.Client') as mock:
        mock_instance = MagicMock()
        mock.return_value = mock_instance
        yield mock_instance

def test_process_ocr_success(mock_client):
    """Probar proceso OCR exitoso."""
    # Simular respuesta exitosa del modelo
    mock_result = (
        "raw_text",
        "markdown_text",
        "additional_info"
    )
    mock_client.predict.return_value = mock_result

    result = process_ocr(
        file_path="test.jpg",
        mode="Gundam",
        task="🔍 Describe",
        custom_prompt="Find text"
    )

    assert result['raw_output'] == mock_result
    assert result['text'] == mock_result[1]  # markdown_text
    assert result['extra']['status'] == 'ok'
    assert result['extra']['mode'] == 'Gundam'
    assert result['extra']['task'] == '🔍 Describe'

def test_process_ocr_error():
    """Probar manejo de errores en proceso OCR."""
    # Simular un error en el proceso
    with patch('hf_client.client.predict', side_effect=Exception("Error de API")):
        result = process_ocr("test.png")
        
        assert 'error' in result
        assert result['status'] == 'failed'
        assert 'Error de API' in result['error']

def test_process_ocr_invalid_file():
    """Probar proceso OCR con archivo inválido."""
    result = process_ocr("archivo_inexistente.jpg")
    assert 'error' in result
    assert result['status'] == 'failed'

def test_process_ocr_default_parameters():
    """Probar valores por defecto de process_ocr."""
    with patch('hf_client.client.predict') as mock_predict:
        process_ocr("test.png")
        
        # Verificar que se llamó con los valores por defecto
        mock_predict.assert_called_once()
        args, kwargs = mock_predict.call_args
        assert kwargs['mode'] == "Gundam"
        assert kwargs['task'] == "🔍 Describe"
        assert kwargs['custom_prompt'] == "Extract text"

def test_environment_space_name():
    """Probar que se usa correctamente la variable de entorno HF_SPACE."""
    expected_space = "merterbak/DeepSeek-OCR-Demo"
    assert os.getenv("HF_SPACE", expected_space) == expected_space

@pytest.mark.integration
def test_client_initialization():
    """
    Prueba de integración: verificar que el cliente se inicializa correctamente.
    Marcada como prueba de integración ya que podría intentar conectarse.
    """
    from hf_client import client
    assert client is not None
    assert hasattr(client, 'predict')
