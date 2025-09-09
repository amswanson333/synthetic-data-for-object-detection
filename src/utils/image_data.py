import os
import cv2
from PIL import Image

def get_image_files(directory):
    '''
    Get a list of image files in a directory.
    '''
    file_ext = ('.png', '.jpg', '.jpeg', '.gif', '.bmp')
    image_files = []
    for file in os.listdir(directory):
        if os.path.splitext(file)[1].lower() in file_ext:
            image_files.append(os.path.join(directory, file))
    return image_files

def is_blank_image(image_path, threshold=10):
    '''
    Check if an image is blank (all pixels below a certain threshold).
    '''
    img = cv2.imread(image_path)
    if img is None:
        return False
    return (img < threshold).all()

def scale_image_down(image_path, max_size):
    '''
    Scale an image down to a maximum size.
    '''
    img = Image.open(image_path)
    width, height = img.size
    if width > max_size[0] or height > max_size[1]:
        img.thumbnail(max_size)
        img.save(image_path)

def image_quadrants(image_path):
    '''
    Divide an image into four quadrants with 5% overlap.
    '''
    img = cv2.imread(image_path)
    height, width = img.shape[:2]
    patch_size = (int(width * 0.55), int(height * 0.55))
    strides = (int(width * 0.45), int(height * 0.45))
    
    quadrants = {
        "top_left": img[0:patch_size[1], 0:patch_size[0]],
        "top_right": img[0:patch_size[1], width - patch_size[0]:width],
        "bottom_left": img[height - patch_size[1]:height, 0:patch_size[0]],
        "bottom_right": img[height - patch_size[1]:height, width - patch_size[0]:width]
    }
    return quadrants