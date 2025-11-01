# OCR DeepSeek - Prueba Técnica

Aplicación web que utiliza el modelo DeepSeek-OCR de Hugging Face para realizar reconocimiento óptico de caracteres (OCR) en imágenes y documentos PDF.

## 🚀 Características

- Interfaz web intuitiva para subir archivos
- Soporte para imágenes y PDFs
- Múltiples modos de OCR:
  - ⚡ Gundam: Balance entre velocidad y precisión
  - 🚀 Tiny: Modo más rápido
  - 📄 Small: Modo ligero
  - 📊 Base: Modo estándar
  - 🎯 Large: Máxima precisión
- Tareas disponibles:
  - 🔍 Describe: Genera una descripción detallada

## 🛠️ Instalación

1. Clonar el repositorio:
```bash
git clone https://github.com/TIGR4X/OCRDeepSeek_PruebaTecnica.git
cd OCRDeepSeek_PruebaTecnica
```

2. Crear y activar entorno virtual (opcional pero recomendado):
1. Clonar el repositorio:

```bash
git clone https://github.com/TIGR4X/OCRDeepSeek_PruebaTecnica.git
cd OCRDeepSeek_PruebaTecnica
```

2. Crear y activar entorno virtual (opcional pero recomendado):

```bash
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

3. Instalar dependencias:

```bash
pip install -r requirements.txt
```

## 🏃‍♂️ Uso

1. Iniciar el servidor Flask:

```bash
python app.py
```

2. Abrir en el navegador:

```
http://localhost:5000
```

3. Usar la interfaz web para:
   - Subir una imagen o PDF
   - Seleccionar el modo de procesamiento
   - Elegir la tarea (Locate o Describe)
   - Procesar y ver resultados

## 🧪 Pruebas

El proyecto incluye pruebas unitarias y de integración exhaustivas.

### Ejecutar Pruebas

1. Ejecutar todas las pruebas:

```bash
pytest tests/ -v
```

2. Ejecutar pruebas específicas:

```bash
# Pruebas de la aplicación Flask
pytest tests/test_app.py -v

# Pruebas del cliente Hugging Face
pytest tests/test_hf_client.py -v

# Excluir pruebas de integración
pytest tests/ -v -m "not integration"
```

### Cobertura de Código

1. Generar reporte de cobertura en consola:

```bash
pytest --cov=. tests/ -v
```

2. Generar reporte HTML detallado:

```bash
pytest --cov=. tests/ -v --cov-report html
```

3. Ver reporte HTML:

```bash
start coverage_html/index.html  # Windows
open coverage_html/index.html   # Mac/Linux
```

### Pruebas de Rendimiento

El proyecto incluye un script de benchmark para evaluar el rendimiento:

```bash
python scripts/benchmark_describe.py [--start-server] [--count N]
```

Opciones:
- `--start-server`: Inicia automáticamente el servidor Flask
- `--count N`: Número de imágenes de prueba (default: 10)

## 📁 Estructura del Proyecto

```
OCRDeepSeek_PruebaTecnica/
├── app.py                 # Servidor Flask principal
├── hf_client.py          # Cliente Hugging Face
├── requirements.txt      # Dependencias
├── templates/            # Plantillas HTML
│   └── index.html       # Interfaz web
├── tests/               # Pruebas unitarias
│   ├── conftest.py     # Configuración pytest
│   ├── test_app.py     # Pruebas de Flask
│   └── test_hf_client.py # Pruebas del cliente HF
├── scripts/             # Scripts útiles
│   └── benchmark_describe.py  # Pruebas de rendimiento
└── uploads/            # Directorio para archivos subidos
```

## ⚙️ Configuración

### Variables de Entorno

Crear archivo `.env` en la raíz:

```env
HF_SPACE=merterbak/DeepSeek-OCR-Demo  # Space de Hugging Face
FLASK_ENV=development
```

### Configuración de Pruebas

El archivo `.coveragerc` configura la cobertura de código:
- Excluye directorios innecesarios
- Configura reporte HTML
- Define líneas a ignorar

## 📊 Métricas y Monitoreo

Los benchmarks generan:
- Archivos JSON por imagen en `results/`
- `results/summary.csv` con métricas por imagen
- `results/summary.json` con estadísticas agregadas:
  - Tiempo promedio de procesamiento
  - Tasa de éxito
  - Tiempos mínimo/máximo

## 🤝 Contribuir

1. Fork el repositorio
2. Crear rama para feature: `git checkout -b feature/NuevaCaracteristica`
3. Commit cambios: `git commit -am 'Agregar nueva característica'`
4. Push a la rama: `git push origin feature/NuevaCaracteristica`
5. Crear Pull Request

## 📝 Notas

- El modelo puede tener limitaciones con:
  - Imágenes muy grandes
  - Textos en ciertos idiomas
  - Fuentes muy decorativas
- Los tiempos de procesamiento varían según el modo seleccionado
