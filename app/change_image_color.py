from PIL import Image
import numpy as np

def protanopia_simulation(image_path):
    image = Image.open(image_path)
    np_image = np.array(image)

    # Transformation matrix for Protanopia
    matrix = np.array([[0.567, 0.433, 0],
                       [0.558, 0.442, 0],
                       [0, 0.242, 0.758]])

    # Apply the matrix transformation
    protanopia_image = np.dot(np_image[...,:3], matrix.T)
    protanopia_image = np.clip(protanopia_image, 0, 255).astype(np.uint8)

    return Image.fromarray(protanopia_image)

# 使用例
protanopia_image = protanopia_simulation('input_image.jpg')
protanopia_image.show()