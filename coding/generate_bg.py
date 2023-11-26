# filename: generate_bg.py
from PIL import Image

# Make sure the size is suitable for your website's layout.
width = 1920
height = 1080

# Initialize a new image
img = Image.new('RGB', (width, height), color='white')

# Create a gradient from white to violet
for y in range(height):
    for x in range(width):
        img.putpixel((x, y), (128 + int(127.0 * y / height), 0, 128 + int(127.0 * y / height)))

# Save the picture. Make sure the directory exists already
img.save("background.png")