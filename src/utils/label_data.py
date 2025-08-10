import os

# Change video annotations to YOLO COCO text format
def convert_annotations(file_name, input_path, output_folder, width, height):
        
    frame_count = 0

    input_file = os.path.join(input_path, f"{file_name}.txt")

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
            output_file = os.path.join(output_folder, f"{file_name}_frame_{frame:04d}.txt")
            with open(output_file, 'a') as outfile:
            
                # Loop for each object in the line
                for i in range(num_objects):
                    start_index = i * 5
                    x_pos = float(parts[start_index])
                    y_pos = float(parts[start_index + 1])
                    bbox_width = float(parts[start_index + 2])
                    bbox_height = float(parts[start_index + 3])
                    class_id = parts[start_index + 4]
                    
                    # Convert class_id to integer
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
                    outfile.write(f"{class_id} {x_center} {y_center} {bbox_width} {bbox_height}")
            
            frame_count += 1
    
    print(f"Wrote {frame_count} annotation files to {output_folder}")