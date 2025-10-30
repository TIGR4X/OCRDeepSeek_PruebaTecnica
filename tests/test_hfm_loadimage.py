from gradio_client import Client, handle_file

client = Client("merterbak/DeepSeek-OCR-Demo")
result = client.predict(
	file_path=handle_file('https://github.com/gradio-app/gradio/raw/main/test/test_files/sample_file.pdf'),
	api_name="/load_image"
)
print(result)