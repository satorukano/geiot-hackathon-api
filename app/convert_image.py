import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
def apply_color_blindness_filter(image, filter_matrix):
    """Apply a color blindness filter to an image."""
    arr = np.array(image)
    filtered_arr = np.tensordot(arr, filter_matrix, axes=([2], [1]))
    filtered_arr = np.clip(filtered_arr, 0, 255).astype(np.uint8)
    return Image.fromarray(filtered_arr)
def simulate_protanopia(image):
    protanopia_matrix = np.array([
        [0.567, 0.433, 0.0],
        [0.558, 0.442, 0.0],
        [0.0, 0.242, 0.758]
    ])
    return apply_color_blindness_filter(image, protanopia_matrix)
def simulate_deuteranopia(image):
    deuteranopia_matrix = np.array([
        [0.625, 0.375, 0.0],
        [0.7, 0.3, 0.0],
        [0.0, 0.3, 0.7]
    ])
    return apply_color_blindness_filter(image, deuteranopia_matrix)
def simulate_tritanopia(image):
    tritanopia_matrix = np.array([
        [0.95, 0.05, 0.0],
        [0.0, 0.433, 0.567],
        [0.0, 0.475, 0.525]
    ])
    return apply_color_blindness_filter(image, tritanopia_matrix)
# Load image
image_path = 'your_image_path.jpg'  # 変換したい画像のパスを指定してください
original_image = Image.open(image_path)
# Apply filters
protanopia_image = simulate_protanopia(original_image)
deuteranopia_image = simulate_deuteranopia(original_image)
tritanopia_image = simulate_tritanopia(original_image)




# Display results
# fig, axes = plt.subplots(1, 4, figsize=(20, 5))
# axes[0].imshow(original_image)
# axes[0].set_title('Original')
# axes[0].axis('off')
# axes[1].imshow(protanopia_image)
# axes[1].set_title('Protanopia')
# axes[1].axis('off')
# axes[2].imshow(deuteranopia_image)
# axes[2].set_title('Deuteranopia')
# axes[2].axis('off')
# axes[3].imshow(tritanopia_image)
# axes[3].set_title('Tritanopia')
# axes[3].axis('off')
# plt.show()