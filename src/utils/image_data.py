import os
import cv2
from PIL import Image

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

def draw_bbox(image_path, bboxes):
    '''
    Draw bounding boxes on an image.
    '''
    img = cv2.imread(image_path)
    width, height = img.shape[1], img.shape[0]
    for bbox in bboxes:
        x1, y1, x2, y2 = bbox
        x1 = int(x1 * width)
        y1 = int(y1 * height)
        x2 = int(x2 * width)
        y2 = int(y2 * height)
        # Draw the rectangle with top left and bottom right points
        cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 0), 2)
        # Add the label
        cv2.putText(img, "Drone", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36,255,12), 2)
    return img