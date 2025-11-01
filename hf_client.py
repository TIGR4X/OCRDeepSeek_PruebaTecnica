import os
from gradio_client import Client, handle_file

# Carga la URL del modelo (puedes reemplazarla por otro Space si quieres)
SPACE_NAME = os.getenv("HF_SPACE", "merterbak/DeepSeek-OCR-Demo")

# Inicializa el cliente
client = Client(SPACE_NAME)


def process_ocr(file_path: str, mode: str = "Gundam", task: str = "📋 Markdown", custom_prompt: str = "Extract text"):
    """
        Envía un archivo (imagen o PDF) al modelo OCR de Hugging Face y devuelve el resultado.
    """
    
    try:
        result = client.predict(
            image=None,  # opcional, el modelo acepta imagen o PDF
            file_path=handle_file(file_path),
            mode=mode,
            task=task,
            custom_prompt=custom_prompt,
            api_name="/run"
        )

        # result es una tupla con varios elementos; el texto OCR suele venir en el índice [1]
        return {
            "raw_output": result,
            "text": result[1],
            "extra": {
                "status": "ok",
                "mode": mode,
                "task": task
            }
        }

    except Exception as e:
        return {"error": str(e), "status": "failed"}
