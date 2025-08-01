import os
import cv2

def to_frames(file_name):
    
    # Define the video path and extract the video name
    # TODO: Update path functions
    video_path = os.path.join(DATA_DIR, file_name)
    video_name = os.path.splitext(os.path.basename(video_path))[0]
    
    # Create the output folder if it does not exist
    output_folder = os.path.join(DATA_DIR, video_name)
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Initialize video capture
    cap = cv2.VideoCapture(video_path)
    frame_count = 0
    
    # Loop through the video frames and save each frame as an image
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame_filename = os.path.join(output_folder, f"{video_name}_frame_{frame_count:04d}.png")
        cv2.imwrite(frame_filename, frame)
        frame_count += 1
    
    # Release the video capture object
    cap.release()
    print(f"Extracted {frame_count} frames to {output_folder}")
    
def get_resolution(file_name):
    # TODO: update path functions
    video_path = os.path.join(DATA_DIR, file_name)
    cap = cv2.VideoCapture(video_path)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()
    return width, height