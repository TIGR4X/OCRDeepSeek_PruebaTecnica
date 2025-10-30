import os
from flask import Flask, render_template, request, jsonify
from hf_client import process_ocr

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/ocr", methods=["POST"])
def api_ocr():
    if "file" not in request.files:
        return jsonify({"error": "No se proporcionó archivo"}), 400

    file = request.files["file"]
    if not file.filename:
        return jsonify({"error": "Nombre de archivo inválido"}), 400

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    task = request.form.get("task", "📋 Markdown")
    mode = request.form.get("mode", "⚡ Gundam")
    prompt = request.form.get("prompt", "Extract text")

    result = process_ocr(filepath, mode=mode, task=task, custom_prompt=prompt)
    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True)
