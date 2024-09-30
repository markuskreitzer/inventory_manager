import qrcode
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
import io

def draw_price_tag(c, x, y, tag_width, tag_height, title, price, url):
    # Draw the tag border
    c.setStrokeColor(colors.black)
    c.rect(x, y, tag_width, tag_height)

    # Generate QR code image
    qr = qrcode.QRCode(box_size=10, border=0)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    # Convert PIL image to a format suitable for ReportLab
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    qr_image = ImageReader(buf)

    # Dimensions for QR code
    qr_size = tag_height - 50  # Adjusted QR code size

    # Position the QR code on the right, centered vertically
    qr_x = x + tag_width - qr_size - 5  # QR code on the right with padding
    qr_y = y + (tag_height - qr_size) / 2  # Centered along the y-axis

    # Draw QR code image
    c.drawImage(qr_image, qr_x, qr_y, qr_size, qr_size)

    # Limit the title to 20 characters
    title = title[:20]

    # Text positioning
    text_x = x + 10  # Padding from left
    text_y = y + tag_height / 2 + 10  # Start a bit above the center

    # Draw Title in Italic
    c.setFont("Helvetica-Oblique", 12)
    c.drawString(text_x, text_y, title)

    # Draw Price
    c.setFont("Helvetica", 10)
    c.setFillColor(colors.black)
    c.drawString(text_x, text_y - 20, f"${price:,}")  # Format price with commas
    c.setFillColor(colors.black)  # Reset color

def create_price_tags_pdf(filename, items):
    # Constants
    page_width, page_height = letter  # 612 x 792 points
    margin = 0.5 * inch  # 36 points
    division = 0.5 * inch  # Space between tags
    tag_width = 3.5 * inch  # 252 points
    tag_height = 2 * inch  # 144 points

    # Calculate number of tags per row and column
    tags_per_row = int((page_width - 2 * margin + division) / (tag_width + division))
    tags_per_column = int((page_height - 2 * margin + division) / (tag_height + division))

    c = canvas.Canvas(filename, pagesize=letter)

    total_tags = len(items)
    tags_per_page = tags_per_row * tags_per_column
    pages = (total_tags + tags_per_page - 1) // tags_per_page  # Ceiling division

    tag_index = 0
    for page in range(pages):
        # Adjust margins to center the tags on the page
        total_tags_width = tags_per_row * tag_width + (tags_per_row - 1) * division
        total_tags_height = tags_per_column * tag_height + (tags_per_column - 1) * division
        left_margin = (page_width - total_tags_width) / 2
        bottom_margin = (page_height - total_tags_height) / 2

        for row in range(tags_per_column):
            for col in range(tags_per_row):
                if tag_index >= total_tags:
                    break  # No more tags to draw
                x = left_margin + col * (tag_width + division)
                y = bottom_margin + (tags_per_column - row - 1) * (tag_height + division)
                item = items[tag_index]
                draw_price_tag(c, x, y, tag_width, tag_height, item['title'], item['price'], item['url'])
                tag_index += 1
            else:
                continue
            break  # Break outer loop if no more tags

        if page < pages - 1:
            c.showPage()  # Create a new page

    c.save()

if __name__ == "__main__":
    # Install required packages if not already installed
    # pip install reportlab qrcode[pil]

    # Sample data
    items = [
        {'title': 'Widget A', 'price': 1000, 'url': 'http://example.com/widget-a'},
        {'title': 'Widget B', 'price': 2000, 'url': 'http://example.com/widget-b'},
        {'title': 'Widget C', 'price': 3000, 'url': 'http://example.com/widget-c'},
        # Add more items as needed
    ]

    # Create the PDF
    create_price_tags_pdf("price_tags.pdf", items)
