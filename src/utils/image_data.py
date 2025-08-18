import os
import cv2
from PIL import Image

def get_image_files(directory):

    file_ext = ('.png', '.jpg', '.jpeg', '.gif', '.bmp')
    image_files = []
    for file in os.listdir(directory):
        if os.path.splitext(file)[1].lower() in file_ext:
            image_files.append(os.path.join(directory, file))
    return image_files

def is_blank_image(image_path, threshold=10):
    
    img = cv2.imread(image_path)
    if img is None:
        return False
    return (img < threshold).all()

def scale_image_down(image_path, max_size):
    
    img = Image.open(image_path)
    img.thumbnail((max_size, max_size), Image.ANTIALIAS)
    img.save(image_path)
