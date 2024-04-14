import json
from PIL import Image, ImageDraw
import os, random

# Define shapes
shapes = ["rectangle", "ellipse", "triangle"]

# Define colors
colors = ["red", "green", "blue", "yellow", "purple", "orange"]


def draw_pattern(draw, shape, primary_color, secondary_color, width, height):
    if shape == "rectangle":
        draw.rectangle(
            [20, 20, width - 20, height - 20],
            fill=primary_color,
            outline=secondary_color,
        )
    elif shape == "ellipse":
        draw.ellipse(
            [20, 20, width - 20, height - 20],
            fill=primary_color,
            outline=secondary_color,
        )
    elif shape == "triangle":
        draw.polygon(
            [width / 2, 20, 20, height - 20, width - 20, height - 20],
            fill=primary_color,
            outline=secondary_color,
        )


def create_feature_image(title, width=400, height=200):
    # Create a blank image with a white background
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)

    # Randomly select features
    primary_shape = random.choice(shapes)
    secondary_shape = random.choice(
        [shape for shape in shapes if shape != primary_shape]
    )
    primary_color = random.choice(colors)
    secondary_color = random.choice(
        [color for color in colors if color != primary_color]
    )

    # Draw primary shape
    draw_pattern(draw, primary_shape, primary_color, secondary_color, width, height)

    # Draw secondary shape with transparency
    overlay = Image.new("RGBA", (width, height), (255, 255, 255, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    draw_pattern(
        overlay_draw,
        secondary_shape,
        secondary_color,
        primary_color,
        width // 2,
        height // 2,
    )
    image.paste(overlay, (width // 4, height // 4), overlay)

    # Save the image
    if not os.path.exists("static/images"):
        os.makedirs("static/images")
    image_path = f"static/images/{title.replace(' ', '_')}.png"
    image.save(image_path)
    return {
        "title": title,
        "file_path": image_path,
        "primary_shape": primary_shape,
        "secondary_shape": secondary_shape,
        "primary_color": primary_color,
        "secondary_color": secondary_color,
        "additional_features": {},  # Add any additional features here
    }


images_data = []
for i in range(1, 101):
    title = f"Image {i}"
    image_data = create_feature_image(title)
    images_data.append(image_data)
    print(f"Generated image saved at {image_data['file_path']}")

# Save the generated image data to a JSON file
images_data_file = os.path.join("static", "images", "images_data.json")
with open(images_data_file, "w") as file:
    json.dump(images_data, file)
