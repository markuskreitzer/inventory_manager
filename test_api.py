import base64
import requests

def send_request(image_path, price, name):
    with open(image_path, 'rb') as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode('utf-8')

    data = {
        'image': encoded_image,
        'price': price,
        'name': name
    }

    response = requests.post('http://localhost:8000/add_item/', json=data)

    print(response.text)

# Example usage:
send_request('/Users/c/Desktop/MammaArt/Web/Sept/Sheep.jpg', 550, 'Cozy Sheep')
