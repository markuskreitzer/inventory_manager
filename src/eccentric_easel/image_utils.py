import base64
from io import BytesIO
from PIL import Image

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def resize_image(image_path):
    with Image.open(image_path) as img:
        max_size = (2000, 2000)  # Maximum dimensions allowed by Square
        img.thumbnail(max_size)  # Resize while maintaining aspect ratio

        # Convert to bytes for uploading
        img_byte_arr = BytesIO()
        img.save(img_byte_arr, format='JPEG')  # Ensure JPEG format
        img_byte_arr.seek(0)
        return img_byte_arr