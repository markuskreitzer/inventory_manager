import argparse
import os
from pathlib import Path

import yaml
from openai import OpenAI
from square.client import Client as SquareClient
from square.http.auth.o_auth_2 import BearerAuthCredentials

from eccentric_easel.ai_utils import generate_image_name, generate_image_description
from eccentric_easel.square_utils import add_item_to_inventory
from eccentric_easel.utils import review_and_confirm


def main():
    # Define command-line arguments
    parser = argparse.ArgumentParser(description="Add an item to Square inventory based on an image.")
    parser.add_argument("image_path", type=Path, help="Path to the image file")
    parser.add_argument("--price", type=int, default=1000, help="Price amount in dollars")
    parser.add_argument("--name", help="Name of the item (if provided, only description will be generated)")
    args = parser.parse_args()

    # Load configuration from YAML file
    config_path = "config/configs.yml"
    try:
        with open(config_path) as config_file:
            config = yaml.safe_load(config_file)
    except FileNotFoundError:
        print(f"Error: Configuration file '{config_path}' not found.")
        return
    except yaml.YAMLError as e:
        print(f"Error parsing configuration file: {e}")
        return

    # Initialize OpenAI and Square clients
    try:
        #openai_client = OpenAI(api_key=os.environ['OPENAI_API_KEY'], base_url='http://localhost:11434/v1')
        openai_client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])
        square_client = SquareClient(
            bearer_auth_credentials=BearerAuthCredentials(access_token=os.environ['SQUARE_APPLICATION_TOKEN']),
            environment='production'
        )
    except KeyError as e:
        print(f"Error: Environment variable '{e}' not set.")
        return

    # Generate item name and description
    try:
        if not args.name:
            #name = generate_image_name(args.image_path, config['name_prompt'], openai_client, model="llava:34b")
            name = generate_image_name(args.image_path, config['name_prompt'], openai_client)
        else:
            name = args.name

        description = generate_image_description(args.image_path, config['description_prompt'], openai_client)
        #description = generate_image_description(args.image_path, config['description_prompt'], openai_client, model="llava:34b")

        if not name or not description:
            raise ValueError("Failed to generate name or description.")
    except Exception as e:
        print(f"Error generating item info: {e}")
        return

    # Get location ID from configuration
    location_id = config.get('LOCATION_IDS', [])[1]  # Eccentric Easel

    confirmed, name, description, args.price = review_and_confirm(name, description, args.price)
    if not confirmed:
        exit()

    try:
        add_item_to_inventory(
            args.image_path,
            name,
            description,
            args.price,
            location_id,  # This argument was missing
            square_client  # This argument was missing
        )
    except Exception as e:
        print(f"Error adding item to catalog: {e}")

if __name__ == "__main__":
    main()
