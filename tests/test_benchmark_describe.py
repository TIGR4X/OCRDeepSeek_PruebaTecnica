"""
Pruebas unitarias para el script de benchmark_describe.py

Ejecutar con:
    pytest test_benchmark_describe.py -v
"""
import os
import json
import tempfile
from pathlib import Path
import pytest
from PIL import Image
import requests
from unittest.mock import patch, MagicMock

# Importar el módulo a probar
import benchmark_describe as bd

@pytest.fixture
def temp_dir():
    """Fixture que provee un directorio temporal para pruebas."""
    with tempfile.TemporaryDirectory() as td:
        yield Path(td)

def test_ensure_dirs(temp_dir):
    """Probar creación de directorios necesarios."""
    # Sobreescribir temporalmente las constantes
    with patch.object(bd, 'SAMPLES_DIR', temp_dir / 'samples'), \
         patch.object(bd, 'RESULTS_DIR', temp_dir / 'results'):
        
        bd.ensure_dirs()
        
        assert (temp_dir / 'samples').exists()
        assert (temp_dir / 'results').exists()

def test_gen_sample_image(temp_dir):
    """Probar generación de imagen de prueba."""
    out_path = temp_dir / 'test_sample.jpg'
    bd.gen_sample_image(out_path, idx=1)
    
    assert out_path.exists()
    img = Image.open(out_path)
    assert img.size == (800, 600)  # verificar dimensiones
    assert img.mode == 'RGB'  # verificar modo de color

def test_generate_samples(temp_dir):
    """Probar generación de múltiples imágenes."""
    with patch.object(bd, 'SAMPLES_DIR', temp_dir / 'samples'):
        paths = bd.generate_samples(count=3)  # probar con 3 imágenes
        
        assert len(paths) == 3
        for p in paths:
            assert p.exists()
            assert p.suffix == '.jpg'

@pytest.fixture
def mock_response():
    """Fixture que simula una respuesta exitosa de requests."""
    mock = MagicMock()
    mock.status_code = 200
    mock.json.return_value = {
        "text": "Una imagen que contiene texto y figuras",
        "extra": {"mode": "Gundam", "task": "🔍 Describe"}
    }
    mock.content = b"mock content"
    return mock

def test_run_benchmark_single_image(temp_dir, mock_response):
    """Probar procesamiento de una sola imagen."""
    # Generar imagen de prueba
    img_path = temp_dir / 'test.jpg'
    bd.gen_sample_image(img_path, idx=0)
    
    # Simular requests.post
    with patch('requests.post', return_value=mock_response), \
         patch.object(bd, 'RESULTS_DIR', temp_dir / 'results'):
        
        summary = bd.run_benchmark([img_path], start_server=False)
        
        # Verificar resumen
        assert summary['total'] == 1
        assert summary['successes'] == 1
        assert isinstance(summary['avg_time_s'], float)
        
        # Verificar archivos generados
        results_dir = temp_dir / 'results'
        assert (results_dir / 'summary.csv').exists()
        assert (results_dir / 'summary.json').exists()
        assert (results_dir / 'test.jpg.json').exists()

def test_run_benchmark_handles_errors(temp_dir):
    """Probar manejo de errores en el benchmark."""
    img_path = temp_dir / 'test.jpg'
    bd.gen_sample_image(img_path, idx=0)
    
    # Simular error de conexión
    with patch('requests.post', side_effect=requests.ConnectionError("Error de conexión")), \
         patch.object(bd, 'RESULTS_DIR', temp_dir / 'results'):
        
        summary = bd.run_benchmark([img_path], start_server=False)
        
        # Verificar que el error se manejó correctamente
        assert summary['total'] == 1
        assert summary['successes'] == 0
        
        # Verificar que se guardó el error en el JSON
        result_file = temp_dir / 'results' / 'test.jpg.json'
        assert result_file.exists()
        with open(result_file) as f:
            result = json.load(f)
            assert 'error' in result
            assert 'conexión' in result['error'].lower()

def test_start_flask_app_process_timeout():
    """Probar timeout al arrancar servidor Flask."""
    with patch('requests.get', side_effect=requests.ConnectionError()), \
         pytest.raises(RuntimeError) as exc_info:
        bd.start_flask_app_process()
    
    assert "No se pudo arrancar el servidor" in str(exc_info.value)

# Pruebas de integración (marcar como tales)
@pytest.mark.integration
def test_full_benchmark_workflow(temp_dir):
    """Prueba de integración del flujo completo."""
    # Sobreescribir paths
    with patch.object(bd, 'SAMPLES_DIR', temp_dir / 'samples'), \
         patch.object(bd, 'RESULTS_DIR', temp_dir / 'results'), \
         patch('requests.post', return_value=mock_response):
        
        # Generar muestras
        paths = bd.generate_samples(count=2)
        assert len(paths) == 2
        
        # Ejecutar benchmark
        summary = bd.run_benchmark(paths, start_server=False)
        
        # Verificar estructura completa de resultados
        results_dir = temp_dir / 'results'
        assert (results_dir / 'summary.csv').exists()
        assert (results_dir / 'summary.json').exists()
        
        # Verificar métricas
        assert summary['total'] == 2
        assert summary['successes'] == 2
        assert all(key in summary for key in ['avg_time_s', 'min_time_s', 'max_time_s'])