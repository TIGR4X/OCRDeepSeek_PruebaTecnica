#!/usr/bin/env python3
"""
scripts/benchmark_describe.py

Prueba automática para la ruta /api/ocr usando la tarea "🔍 Describe".

Qué hace:
- Genera 10 imágenes de muestra (si no existen) en tests/samples/
- Opcionalmente arranca el servidor Flask (importando app.py) en un proceso hijo
- Envía cada imagen vía POST multipart/form-data a http://localhost:5000/api/ocr
- Mide tiempos de respuesta, tamaño y estado
- Guarda resultados JSON individuales en results/ y un resumen CSV/JSON

Uso:
  python scripts/benchmark_describe.py [--start-server]

Notas:
- Requiere que las dependencias incluidas en requirements.txt estén instaladas (requests, Pillow)
"""
import os
import sys
import time
import json
import csv
import argparse
from pathlib import Path
from multiprocessing import Process
from PIL import Image, ImageDraw, ImageFont
import requests

ROOT = Path(__file__).resolve().parents[1]
SAMPLES_DIR = ROOT / 'tests' / 'samples'
RESULTS_DIR = ROOT /'tests' /'results'
API_URL = 'http://127.0.0.1:5000/api/ocr'

SAMPLE_COUNT = 10


def ensure_dirs():
    SAMPLES_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def gen_sample_image(path: Path, idx: int):
    """Genera una imagen sintética con texto y elementos variados."""
    w, h = 800, 600
    img = Image.new('RGB', (w, h), color=(255, 255, 255))
    d = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype('arial.ttf', 28)
    except Exception:
        font = ImageFont.load_default()

    # Texto principal
    d.text((20, 20), f'Sample #{idx+1} - Prueba OCR', font=font, fill=(0, 0, 0))

    # Añadir distintas líneas
    for i in range(6):
        y = 80 + i * 60
        d.text((30, y), f'Linea {i+1} del documento de prueba. Valor: {idx * 100 + i}', font=font, fill=(10, 10, 10))

    # Dibujar una caja/figura para simular área de interés
    d.rectangle([550, 50, 760, 200], outline=(200, 30, 30), width=4)
    d.text((560, 60), 'Figura', font=font, fill=(200, 30, 30))

    img.save(path, format='JPEG', quality=85)


def generate_samples(count=SAMPLE_COUNT):
    ensure_dirs()
    paths = []
    for i in range(count):
        p = SAMPLES_DIR / f'sample_{i+1}.jpg'
        if not p.exists():
            gen_sample_image(p, i)
        paths.append(p)
    return paths


def start_flask_app_process():
    """Arranca el server Flask importando app.py en un proceso separado.

    Requiere que el módulo `app` exporte la instancia `app` (Flask).
    """
    sys.path.insert(0, str(ROOT))
    try:
        import app as flask_app_module

        def run_app():
            flask_app_module.app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False)

        p = Process(target=run_app, daemon=True)
        p.start()

        # esperar a que el servidor responda (max ~15s)
        for _ in range(30):
            try:
                r = requests.get('http://127.0.0.1:5000', timeout=1)
                if r.status_code == 200:
                    return p
            except Exception:
                time.sleep(0.5)
        p.terminate()
        raise RuntimeError('No se pudo arrancar el servidor Flask desde app.py')
    except Exception:
        raise


def run_benchmark(image_paths, start_server=False):
    server_proc = None
    if start_server:
        print('Iniciando servidor Flask desde app.py...')
        server_proc = start_flask_app_process()
        print(f'Servidor arrancado (PID {server_proc.pid}).')

    results = []

    for p in image_paths:
        print(f'Procesando {p.name} ...')
        with open(p, 'rb') as fh:
            files = {'file': (p.name, fh, 'image/jpeg')}
            data = {'mode': 'Gundam', 'task': '🔍 Describe', 'prompt': ''}

            t0 = time.perf_counter()
            try:
                resp = requests.post(API_URL, files=files, data=data, timeout=120)
                elapsed = time.perf_counter() - t0
                status = resp.status_code
                try:
                    payload = resp.json()
                except Exception:
                    payload = {'raw_text': resp.text}

                out = {
                    'image': str(p),
                    'status_code': status,
                    'time_s': elapsed,
                    'payload': payload,
                    'response_size': len(resp.content) if resp is not None else 0
                }
                print(f' -> {status}, {elapsed:.2f}s')
            except Exception as e:
                elapsed = time.perf_counter() - t0
                out = {
                    'image': str(p),
                    'status_code': None,
                    'time_s': elapsed,
                    'error': str(e),
                    'payload': None,
                    'response_size': 0
                }
                print(f' -> ERROR: {e}')

        results.append(out)
        safe_name = Path(out['image']).name
        with open(RESULTS_DIR / f'{safe_name}.json', 'w', encoding='utf-8') as fh:
            json.dump(out, fh, ensure_ascii=False, indent=2)

    # resumen CSV
    csv_path = RESULTS_DIR / 'summary.csv'
    keys = ['image', 'status_code', 'time_s', 'response_size']
    with open(csv_path, 'w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=keys)
        w.writeheader()
        for r in results:
            w.writerow({k: r.get(k) for k in keys})

    # métricas simples
    times = [r['time_s'] for r in results if r.get('time_s') is not None]
    successes = sum(1 for r in results if r.get('status_code') == 200)
    total = len(results)
    summary = {
        'total': total,
        'successes': successes,
        'avg_time_s': (sum(times) / len(times)) if times else None,
        'min_time_s': min(times) if times else None,
        'max_time_s': max(times) if times else None
    }
    with open(RESULTS_DIR / 'summary.json', 'w', encoding='utf-8') as fh:
        json.dump({'summary': summary, 'results_count': len(results)}, fh, ensure_ascii=False, indent=2)

    print('\n--- Benchmark completo ---')
    print(json.dumps(summary, indent=2))

    if server_proc:
        print('Deteniendo servidor arrancado por la prueba...')
        server_proc.terminate()

    return summary


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--start-server', action='store_true', help='Arrancar el servidor Flask desde app.py antes de hacer las peticiones')
    parser.add_argument('--count', type=int, default=SAMPLE_COUNT, help='Cantidad de imágenes a generar/probar')
    args = parser.parse_args()

    paths = generate_samples(count=args.count)
    run_benchmark(paths, start_server=args.start_server)


if __name__ == '__main__':
    main()
