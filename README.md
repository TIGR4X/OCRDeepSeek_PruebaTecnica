# OCR App - Hugging Face API Demo

Aplicación Flask que se conecta a un modelo OCR alojado en **Hugging Face Spaces** (`merterbak/DeepSeek-OCR-Demo`) mediante la librería `gradio_client`.

Permite subir imágenes o PDFs, seleccionar el tipo de tarea y obtener el texto extraído o descripción correspondiente.

## 🚀 Instalación

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```