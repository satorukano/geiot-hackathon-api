import numpy as np
import PIL.Image
from PIL import Image  # これを追加
from matplotlib import pylab as P
import torch
from torchvision import models, transforms
import os
import saliency.core as saliency


def save_image(data, filename):
    image = Image.fromarray(data)
    image.save(filename)

def convert_rgba_to_rgb(image):
    if image.shape[2] == 4:
        rgb_image = image[:, :, :3]
        return rgb_image
    else:
        return image

def load_image(file_path):
    im = PIL.Image.open(file_path)
    im = im.resize((299, 299))
    im = np.asarray(im)
    return im

def preprocess_images(images):
    transformer = transforms.Normalize((0.485, 0.456, 0.406), (0.229, 0.224, 0.225))
    images = np.array(images)
    images = images / 255
    images = np.transpose(images, (0, 3, 1, 2))
    images = torch.tensor(images, dtype=torch.float32)
    images = transformer.forward(images)
    return images.requires_grad_(True)

def call_model_function(images, call_model_args=None, expected_keys=None):
    images = preprocess_images(images)
    target_class_idx = call_model_args[class_idx_str]
    output = model(images)
    m = torch.nn.Softmax(dim=1)
    output = m(output)
    if saliency.base.INPUT_OUTPUT_GRADIENTS in expected_keys:
        outputs = output[:, target_class_idx]
        grads = torch.autograd.grad(outputs, images, grad_outputs=torch.ones_like(outputs))
        grads = torch.movedim(grads[0], 1, 3)
        gradients = grads.detach().numpy()
        return {saliency.base.INPUT_OUTPUT_GRADIENTS: gradients}
    else:
        one_hot = torch.zeros_like(output)
        one_hot[:, target_class_idx] = 1
        model.zero_grad()
        output.backward(gradient=one_hot, retain_graph=True)
        return conv_layer_outputs

def generate_saliency_maps(image_path):
    im_orig = load_image(image_path)
    im_orig = convert_rgba_to_rgb(im_orig)
    im_tensor = preprocess_images([im_orig])

    predictions = model(im_tensor)
    predictions = predictions.detach().numpy()
    prediction_class = np.argmax(predictions[0])
    call_model_args = {class_idx_str: prediction_class}

    im = im_orig.astype(np.float32)
    xrai_object = saliency.XRAI()
    xrai_attributions = xrai_object.GetMask(im, call_model_function, call_model_args, batch_size=20)

    mask = xrai_attributions >= np.percentile(xrai_attributions, 70)
    im_mask = np.array(im_orig)
    im_mask[~mask] = 0

    return xrai_attributions, im_mask

def show_heatmap(im, title, save_path=None):
    fig, ax = P.subplots()
    ax.axis('off')
    ax.imshow(im, cmap='inferno')
    ax.set_title(title)
    if save_path:
        fig.savefig(save_path, bbox_inches='tight')
    fig.canvas.draw()
    
    heatmap_image = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
    heatmap_image = heatmap_image.reshape(fig.canvas.get_width_height()[::-1] + (3,))
    
    P.close(fig)
    
    return heatmap_image

def show_image(im, title, save_path=None):
    fig, ax = P.subplots()
    ax.axis('off')
    ax.imshow(im)
    ax.set_title(title)
    if save_path:
        fig.savefig(save_path, bbox_inches='tight')
    fig.canvas.draw()
    
    image = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
    image = image.reshape(fig.canvas.get_width_height()[::-1] + (3,))
    
    P.close(fig)
    
    return image

def generate_saliency_maps_images(image_path):
    # Load the model
    global model
    model = models.inception_v3(pretrained=True, init_weights=False)
    eval_mode = model.eval()

    # Register hooks for Grad-CAM
    global conv_layer_outputs
    conv_layer = model.Mixed_7c
    conv_layer_outputs = {}
    def conv_layer_forward(m, i, o):
        conv_layer_outputs[saliency.base.CONVOLUTION_LAYER_VALUES] = torch.movedim(o, 1, 3).detach().numpy()
    def conv_layer_backward(m, i, o):
        conv_layer_outputs[saliency.base.CONVOLUTION_OUTPUT_GRADIENTS] = torch.movedim(o[0], 1, 3).detach().numpy()
    conv_layer.register_forward_hook(conv_layer_forward)
    conv_layer.register_full_backward_hook(conv_layer_backward)

    global class_idx_str
    class_idx_str = 'class_idx_str'

    # Create output directory if it doesn't exist
    # output_dir = 'image/saliency'
    # os.makedirs(output_dir, exist_ok=True)

    # Generate saliency maps
    xrai_attributions, im_mask = generate_saliency_maps(image_path)

    # Show XRAI heatmap attributions and Top 30% images, and save them
    heatmap_image = show_heatmap(xrai_attributions, title='XRAI Heatmap') #, save_path=os.path.join(output_dir, 'xrai_heatmap.png'))
    top_30_percent_image = show_image(im_mask, title='Top 30%') #, save_path=os.path.join(output_dir, 'top_30_percent.png'))
    return [heatmap_image, top_30_percent_image]


def main():
    images = generate_saliency_maps_images('sample.png')
    
    save_image(images[0], os.path.join('image/saliency', 'heatmap_image.png'))
    save_image(images[1], os.path.join('image/saliency', 'top_30.png'))

if __name__ == '__main__':
    main()
