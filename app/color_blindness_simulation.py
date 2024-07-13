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

def create_blindness_image(image_path, color_blindness_type='deuteranopia', save_path='output_image.png'):
    # Load image
    original_image = Image.open(image_path)
    
    # Apply filters
    if color_blindness_type == 'protanopia':
        processed_image = simulate_protanopia(original_image)
    elif color_blindness_type == 'deuteranopia':
        processed_image = simulate_deuteranopia(original_image)
    elif color_blindness_type == 'tritanopia':
        processed_image = simulate_tritanopia(original_image)
    else:
        raise ValueError("Invalid color blindness type. Choose from 'protanopia', 'deuteranopia', or 'tritanopia'.")
    
    # Save the processed image as PNG
    processed_image.save(save_path, "PNG")

# 使用例
create_blindness_image("many.jpg", color_blindness_type='tritanopia', save_path='output.png')
