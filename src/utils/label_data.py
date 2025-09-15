from cProfile import label
import os

# Change video annotations to YOLO COCO text format
def convert_annotations(file_name, input_path, output_folder, width, height):
        
    frame_count = 0

    text_file_name = os.path.splitext(file_name)[0]
    input_file = os.path.join(input_path, f"{text_file_name}.txt")
    
    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Create/open the input annotation file
    with open(input_file, 'r') as infile:
        # Each line in the input file corresponds to a single frame
        for line in infile:
            parts = line.split()
            
            frame = int(parts.pop(0))  # Remove the frame number from the parts
            num_objects = int(parts.pop(0)) # Remove the number of objects from the parts
            
            # Remaining parts will be in the format: Position_X Position_Y Width Height Class_ID
            # Each object begins at an index multiple of 5
            
            # Create the output file
            output_file = os.path.join(output_folder, f"{text_file_name}_frame_{frame:04d}.txt")
            
            with open(output_file, 'a') as outfile:
                # Loop for each object in the line
                for i in range(num_objects):
                    
                    object_details = parts[i * 5:i * 5 + 5]
                    x_pos = float(object_details[0])
                    y_pos = float(object_details[1])
                    bbox_width = float(object_details[2])
                    bbox_height = float(object_details[3])
                    class_id = object_details[4]

                    # Convert class_id to integer (all labels should be drone)
                    class_id = 0 if class_id == 'drone' else 1
                    
                    # Convert position coordinates to bounding box center
                    x_center = x_pos + bbox_width / 2
                    y_center = y_pos + bbox_height / 2
                    
                    # Normalize the coordinates to the range [0, 1]
                    x_center /= width
                    y_center /= height
                    bbox_width /= width
                    bbox_height /= height
                        
                    # Write the YOLO format to the output file
                    outfile.write(f"{class_id} {x_center} {y_center} {bbox_width} {bbox_height}\n")
            
            frame_count += 1
    
    print(f"Wrote {frame_count} annotation files to {output_folder}")
    
    
def frame_overview(directory):
    
    frames = []
    empty_frames = []
    file_names = []
    
    for file_name in os.listdir(directory):
        zero_count = 0
        line_count = 0
        if file_name.endswith('.txt'):
            with open(os.path.join(directory, file_name), 'r') as file:
                for line in file:
                    line_count += 1
                    parts = line.split()
                    if len(parts) > 1 and parts[1] == '0':
                        zero_count += 1
            frames.append(line_count)
            empty_frames.append(zero_count)
            file_names.append(file_name)
            
    return file_names, empty_frames, frames

def bbox_area(bbox):
    '''
    Calculate the area of a bounding box.
    '''
    _, x_center, y_center, width, height = map(float, bbox)
    return width * height

def read_bbox_file(file_path):
    '''
    Read bounding boxes from a text file.
    '''
    bboxes = []
    with open(file_path, 'r') as file:
        for line in file:
            parts = line.split()
            if len(parts) == 5:
                bboxes.append(parts)
    return bboxes

def bbox_info(bbox):
    '''
    Get information about a bounding box.
    '''
    label, x_center, y_center, width, height = map(float, bbox)
    return {
        "label": label,
        "x_center": x_center,
        "y_center": y_center,
        "width": width,
        "height": height,
        "area": bbox_area(bbox)
    }

def bbox_xxyy(bbox):
    '''
    Convert a bounding box from YOLO format (x_center, y_center, width, height)
    to (x1, y1, x2, y2) format.
    '''
    _, x_center, y_center, width, height = map(float, bbox)
    x1 = x_center - width / 2
    y1 = y_center - height / 2
    x2 = x_center + width / 2
    y2 = y_center + height / 2
    return (x1, y1, x2, y2)

def bbox_yolo(bbox):
    '''
    Convert a bounding box from (x1, y1, x2, y2) to YOLO format (x_center, y_center, width, height).
    '''
    x1, y1, x2, y2 = map(float, bbox)
    x_center = (x1 + x2) / 2
    y_center = (y1 + y2) / 2
    width = x2 - x1
    height = y2 - y1
    # Note that class is hard-coded to 0 (drone)
    return (0, x_center, y_center, width, height)

def bbox_quadrants(bboxes):
    '''
    Divide a bounding box into 4 quadrants.
    '''
    # Holder for the bounding boxes in each quadrant
    quadrants = {
        "top_left": [],
        "top_right": [],
        "bottom_left": [],
        "bottom_right": []
    }
    # Loop through all bounding boxes provided
    for bbox in bboxes:
        original_area = bbox_area(bbox)
        x1, y1, x2, y2 = bbox_xxyy(bbox)
        
        top_left = (
            x1 / 0.55, # Bounding boxes beyond the 0.55 cutoff will be >1
            y1 / 0.55, # Bounding boxes beyond the 0.55 cutoff will be >1
            min(x2, 0.55) / 0.55, # Bounding boxes beyond the 0.55 cutoff will be = 1
            min(y2, 0.55) / 0.55 # Bounding boxes beyond the 0.55 cutoff will be = 1
        )
        top_left_area = (top_left[2] - top_left[0]) * (top_left[3] - top_left[1])
        top_left_area_ratio = top_left_area / original_area if original_area > 0 else 0

        top_right = (
            (max(x1, 0.45) - 0.45) / 0.55, # Bounding boxes beyond the 0.45 cutoff will be = 0
            y1 / 0.55, # Bounding boxes beyond the 0.55 cutoff will be >1
            (x2 - 0.45) / 0.55, # Bounding boxes beyond the 0.45 cutoff will be <0
            min(y2, 0.55) / 0.55 # Bounding boxes beyond the 0.55 cutoff will be = 1
        )
        top_right_area = (top_right[2] - top_right[0]) * (top_right[3] - top_right[1])
        top_right_area_ratio = top_right_area / original_area if original_area > 0 else 0

        bottom_left = (
            x1 / 0.55, 
            (max(y1, 0.45) - 0.45) / 0.55, 
            min(x2, 0.55) / 0.55, 
            (y2 - 0.45) / 0.55
        )
        bottom_left_area = (bottom_left[2] - bottom_left[0]) * (bottom_left[3] - bottom_left[1])
        bottom_left_area_ratio = bottom_left_area / original_area if original_area > 0 else 0

        bottom_right = (
            (max(x1, 0.45) - 0.45) / 0.55, 
            (max(y1, 0.45) - 0.45) / 0.55, 
            (x2 - 0.45) / 0.55, 
            (y2 - 0.45) / 0.55
        )
        bottom_right_area = (bottom_right[2] - bottom_right[0]) * (bottom_right[3] - bottom_right[1])
        bottom_right_area_ratio = bottom_right_area / original_area if original_area > 0 else 0

        # Check if the quadrants are valid and meet the area ratio criteria
        if all(0 <= n <= 1 for n in top_left) and top_left_area_ratio > 0.1:
            quadrants["top_left"].append(top_left)
        if all(0 <= n <= 1 for n in top_right) and top_right_area_ratio > 0.1:
            quadrants["top_right"].append(top_right)
        if all(0 <= n <= 1 for n in bottom_left) and bottom_left_area_ratio > 0.1:
            quadrants["bottom_left"].append(bottom_left)
        if all(0 <= n <= 1 for n in bottom_right) and bottom_right_area_ratio > 0.1:
            quadrants["bottom_right"].append(bottom_right)

    return quadrants