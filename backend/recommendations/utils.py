from PIL import Image
import numpy as np

def calculate_similarity(image1, image2):


    # Load images
    img1 = Image.open(image1)
    img2 = Image.open(image2)

    # Convert images to numpy arrays
    img1_arr = np.array(img1)
    img2_arr = np.array(img2)

    # Calculate the mean squared error
    mse = np.mean((img1_arr - img2_arr) ** 2)

    # If the MSE is 0, the images are exactly the same
    if mse == 0:
        return 1.0

    # Otherwise, calculate the Structural Similarity Index (SSI)
    ssi = 1 - mse / (np.std(img1_arr) * np.std(img2_arr))

    return ssi