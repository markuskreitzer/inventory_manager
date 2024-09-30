import os
from pathlib import Path
from typing import Optional
import base64
from io import BytesIO
from PIL import Image

import yaml
from fastapi import FastAPI
from openai import OpenAI
from pydantic import BaseModel
from typer import Typer, Option

from eccentric_easel.ai_utils import generate_image_name, generate_image_description
from eccentric_easel.square_utils import post_item_to_catalog
from eccentric_easel.utils import review_and_confirm

app = FastAPI()
cli = Typer()

class ItemRequest(BaseModel):
    image: str
    price: int = 1000
    name: Optional[str] = None

def generate_item_info(image_path: Path, price: int, name: Optional[str] = None) -> tuple:
    config_path = "config/configs.yml"
    try:
        with open(config_path) as config_file:
            config = yaml.safe_load(config_file)
    except FileNotFoundError:
        raise ValueError(f"Configuration file '{config_path}' not found.")
    except yaml.YAMLError as e:
        raise ValueError(f"Error parsing configuration file: {e}")

    # Initialize OpenAI client
    try:
        openai_client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])
    except KeyError as e:
        raise ValueError(f"Environment variable '{e}' not set.")

    # Generate item name and description
    try:
        if not name:
            name = generate_image_name(image_path, config['name_prompt'], openai_client)
        else:
            name = name

        description = generate_image_description(image_path, config['description_prompt'], openai_client)

        if not name or not description:
            raise ValueError("Failed to generate name or description.")
    except Exception as e:
        raise ValueError(f"Error generating item info: {e}")

    return name, description

@cli.command()
def add_item(
    image_path: Path = Option(..., help="""Path to the image file. This can be a JPEG, PNG, or GIF file. The image will be resized to fit the catalog's image size requirements."""),
    price: int = Option(1000, help="Price of the item in dollars"),
    name: str = Option(None, help="Name of the item"),
):
    """Add an item to Square inventory based on an image."""
    try:
        name, description = generate_item_info(image_path, price, name)
        confirmed, name, description, price = review_and_confirm(name, description, price)
        if confirmed:
            post_item_to_catalog(image_path, name, description, price)
    except ValueError as e:
        print(f"Error: {e}")

@app.post("/add_item/")
async def add_item_api(item_request: ItemRequest):
    """Add an item to Square inventory based on an image."""
    try:
        # Decode the base64 encoded image
        image_bytes = base64.b64decode(item_request.image)
        image = Image.open(BytesIO(image_bytes))
        image_path = Path("temp_image.jpg")
        image.save(image_path)

        name, description = generate_item_info(image_path, item_request.price, item_request.name)
        post_item_to_catalog(image_path, name, description, item_request.price)
        return {"message": "Item added successfully",
                "name": name,
                "description": description,
                "price": item_request.price
                }
    except Exception as e:
        return {"error": f"Error adding item to catalog: {e}"}
    finally:
        # Remove the temporary image file
        image_path.unlink()

if __name__ == "__main__":
    cli()