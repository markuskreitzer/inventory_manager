# Eccentric Easel Inventory Manager
Manage inventory with Square's API. This program has the following features:
  - Takes a local image, sends it to OpenAI/Ollama Llava and writes a title (optional) and a description.
  - Adds the item to your Square inventory with a stock count of one.
  - Generates a PDF with: QR code, Title, and price of item.

The project uses poetry to manage dependencies and environment. To run, use the `poetry run {verb}` syntax. It also contains an API written with FastAPI.


Future Work:
  - Add a WebUI to connect to from phone.

Needed:
  - Local Ollama instance with Llava running (haven't tested with Llama 3.2 vision yet).
  - OpenAI API key.
  - Square API key.

