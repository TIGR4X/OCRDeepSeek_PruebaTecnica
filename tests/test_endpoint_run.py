from gradio_client import Client, handle_file

client = Client("merterbak/DeepSeek-OCR-Demo")
result = client.predict(
	image=handle_file('https://raw.githubusercontent.com/gradio-app/gradio/main/test/test_files/bus.png'),
	file_path=handle_file('https://raw.githubusercontent.com/gradio-app/gradio/main/test/test_files/bus.png'),
	mode="Gundam",
	task="📋 Markdown",
	custom_prompt="Hello!!",
	api_name="/run"
)
print(result)