from PIL import Image
import numpy as np

def preprocess_image(image_path, binary_path):
    # Load the image and convert to grayscale
    image = Image.open(image_path).convert("L")

    # Resize to (28, 28)
    image = image.resize((28, 28))

    # Convert to float32 and normalize to [0,1]
    image = np.array(image, dtype=np.float32) / 255.0

    # Write to binary file
    with open(binary_path, 'wb') as f:
        f.write(image.tobytes())