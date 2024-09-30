import os
import uuid
from datetime import datetime
from pathlib import Path
from pprint import pprint

import yaml
#import base64

from square.client import Client as SquareClient
from square.http.auth.o_auth_2 import BearerAuthCredentials


# from eccentric_easel.image_utils import resize_image


def post_item_to_catalog(image_path: Path, name: str, description: str, price: int):
    config_path = "config/configs.yml"
    try:
        with open(config_path) as config_file:
            config = yaml.safe_load(config_file)
    except FileNotFoundError:
        raise ValueError(f"Configuration file '{config_path}' not found.")
    except yaml.YAMLError as e:
        raise ValueError(f"Error parsing configuration file: {e}")

    # Initialize Square client
    try:
        square_client = SquareClient(
            bearer_auth_credentials=BearerAuthCredentials(access_token=os.environ['SQUARE_APPLICATION_TOKEN']),
            environment='production'
        )
    except KeyError as e:
        raise ValueError(f"Environment variable '{e}' not set.")

    # Get location ID from configuration
    location_id = config.get('LOCATION_IDS', [])[1]  # Eccentric Easel

    try:
        add_item_to_inventory(
            image_path,
            name,
            description,
            price,
            location_id,
            square_client
        )
    except Exception as e:
        raise ValueError(f"Error adding item to catalog: {e}")


def add_item_to_inventory(image_path: Path,
                          name: str,
                          description: str,
                          amount: int,
                          location_id: str,
                          square_client: SquareClient
                          ):
    random_id = f"#{os.urandom(4).hex()}"
    item_data = {
        "type": "ITEM",
        "id": random_id,
        "present_at_all_locations": True,
        "item_data": {
            "name": name,
            "description": description,
            "is_taxable": True,
            "available_online": True,
            "available_for_pickup": True,
            "variations": [
                {
                    "type": "ITEM_VARIATION",
                    "id": f"{random_id}-variation",
                    "item_variation_data": {
                        "item_id": random_id,
                        "name": name,
                        "pricing_type": "FIXED_PRICING",
                        "price_money": {
                            "amount": amount * 100,
                            "currency": "USD"
                        },
                        "track_inventory": True,
                        "sellable": True
                    }
                }
            ],
            "product_type": "REGULAR",
            "skip_modifier_screen": True
        }
    }

    result = square_client.catalog.upsert_catalog_object(
        body={
            "idempotency_key": uuid.uuid4().hex,
            "object": item_data
        }
    )

    if result.is_success():
        print(f"Successfully added item: {name}")
        #pprint(result.body, indent=2)
        catalog_id = result.body['catalog_object']['id']
        catalog_variation_id = result.body['catalog_object']['item_data']['variations'][0]['id']
        print(f"Catalog ID: {catalog_id}")
        print(f"Catalog Variation ID: {catalog_variation_id}")
        update_inventory(catalog_variation_id, location_id, square_client)
        upload_image_to_square(image_path, catalog_id, name, description, square_client)
    else:
        raise ValueError(f"Error adding item: {result.errors}")


def update_inventory(catalog_object_id: str, location_id: str, square_client: SquareClient):
    inventory_result = square_client.inventory.batch_change_inventory(
        body={
            "idempotency_key": os.urandom(32).hex(),
            "changes": [
                {
                    "type": "ADJUSTMENT",
                    "adjustment": {
                        "from_state": "NONE",
                        "to_state": "IN_STOCK",
                        "location_id": location_id,
                        "catalog_object_id": catalog_object_id,
                        "quantity": "1",
                        "occurred_at": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
                    }
                }
            ]
        }
    )

    if inventory_result.is_success():
        print("Successfully added 1 item to inventory")
    else:
        raise ValueError(f"Error adding inventory: {inventory_result.errors}")


def upload_image_to_square(image_path: Path, item_id, name: str, description: str, square_client):
    try:
        #img_byte_arr = resize_image(image_path)
        #image_data = base64.b64encode(img_byte_arr.read()).decode('utf-8')

        response = square_client.catalog.create_catalog_image(
            request = {
                "idempotency_key": os.urandom(32).hex(),
                "object_id": item_id,
                "image": {
                    "type": "IMAGE",
                    "id": "#1234",
                    "image_data": {
                        "name": name,
                        "caption": description,
                        #"file_name": image_path.name,
                        #"image": image_data
                    }
                },
                "is_primary": True
            },
            image_file=image_path.open('rb')
        )

        if response.is_success():
            print("Image successfully uploaded and linked to item.")
            #pprint(response.body, indent=2)
            return response.body['image']['id']
        elif response.is_error():
            print(response.errors)
            raise ValueError(f"Failed to upload image: {response.errors}")
        else:
            raise ValueError(f"Failed to upload image: {response.errors}")

    except Exception as e:
        print(f"An error occurred while uploading the image: {e}")
        raise
