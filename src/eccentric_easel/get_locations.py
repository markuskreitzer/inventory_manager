import os
from typing import Any

from square.client import Client
from square.http.auth.o_auth_2 import BearerAuthCredentials


def get_locations(client: Client) -> Any | None:
    result = client.locations.list_locations()

    if result.is_success():
        locations = result.body['locations']
        for location in locations:
            print(f"{location['id']}: ", end="")
            print(f"{location['name']}, ", end="")
            print(f"{location['address']['address_line_1']}, ", end="")
            print(f"{location['address']['locality']}")
        return locations
    elif result.is_error():
        for error in result.errors:
            print(error['category'])
            print(error['code'])
            print(error['detail'])
        return None

if __name__ == '__main__':
    client = Client(
        bearer_auth_credentials=BearerAuthCredentials(
            access_token=os.environ['SQUARE_APPLICATION_TOKEN']
        ),
        environment='production')
    get_locations(client)

