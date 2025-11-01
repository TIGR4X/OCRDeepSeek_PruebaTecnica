from gradio_client import Client, handle_file

client = Client("merterbak/DeepSeek-OCR-Demo")
result = client.predict(
	file_path=handle_file('https://raw.githubusercontent.com/gradio-app/gradio/main/test/test_files/bus.png'),
	api_name="/load_image"
)
print(result)