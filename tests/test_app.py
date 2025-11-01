"""
Pruebas unitarias para los componentes principales de la aplicación OCR.

Ejecutar con:
    pytest test_app.py -v
"""
import os
import sys
import json
from io import BytesIO
from pathlib import Path
import pytest
from PIL import Image
from unittest.mock import patch, MagicMock

# Asegurar que el directorio raíz del proyecto esté en el PYTHONPATH
PROJECT_ROOT = Path(__file__).parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app import app

@pytest.fixture
def client():
    """Fixture que proporciona un cliente de prueba para la API Flask."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def sample_image():
    """Fixture que genera una imagen de prueba en memoria."""
    img = Image.new('RGB', (100, 100), color='white')
    img_io = BytesIO()
    img.save(img_io, 'JPEG')
    img_io.seek(0)
    return img_io

def test_index_route(client):
    """Probar que la ruta principal devuelve el template HTML."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'OCR Demo App' in response.data

def test_ocr_route_no_file(client):
    """Probar el endpoint OCR sin archivo."""
    response = client.post('/api/ocr')
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
    assert 'No se proporcionó archivo' in data['error']

def test_ocr_route_empty_filename(client):
    """Probar el endpoint OCR con nombre de archivo vacío."""
    response = client.post('/api/ocr', data={
        'file': (BytesIO(), '')
    })
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
    assert 'Nombre de archivo inválido' in data['error']

def test_ocr_route_success(client, sample_image):
    """Probar el endpoint OCR con una imagen válida."""
    # Mockear la función process_ocr para simular respuesta exitosa
    mock_result = {
        "raw_output": ["Texto extraído", "Texto en markdown", ""],
        "text": "Texto extraído",
        "extra": {
            "status": "ok",
            "mode": "Gundam",
            "task": "🔍 Describe"
        }
    }

    with patch('app.process_ocr', return_value=mock_result):
        response = client.post('/api/ocr', 
            data={
                'file': (sample_image, 'test.jpg'),
                'mode': 'Gundam',
                'task': '🔍 Describe',
                'prompt': 'Test prompt'
            })
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['text'] == "Texto extraído"
        assert data['extra']['status'] == "ok"
        assert data['extra']['mode'] == "Gundam"

def test_upload_folder_creation():
    """Probar que se crea el directorio de uploads."""
    import app
    assert os.path.exists(app.UPLOAD_FOLDER)
