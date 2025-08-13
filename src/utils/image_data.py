import os
import cv2

def get_image_files(directory):

    file_ext = ['.png', '.jpg', '.jpeg', '.gif', '.bmp']
    image_files = []
    for file in os.listdir(directory):
        if file.lower().endswith(file_ext):
            image_files.append(os.path.join(directory, file))
    return image_files

def is_blank_image(directory, image, threshold=10):
    
    img = cv2.imread(os.path.join(directory, image))
    if img is None:
        return False
    return (img < threshold).all()

