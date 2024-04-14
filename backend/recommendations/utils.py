from PIL import Image
import numpy as np


def calculate_similarity(image1, image2):
    img1 = Image.open(image1)
    img2 = Image.open(image2)

    img1_arr = np.array(img1)
    img2_arr = np.array(img2)

    mse = np.mean((img1_arr - img2_arr) ** 2)

    if mse == 0:
        return 1.0

    ssi = 1 - mse / (np.std(img1_arr) * np.std(img2_arr))

    return ssi
