import os
import cv2

def to_frames(file_name, input_folder, output_folder):
    '''
    Convert a video file to individual frames.
    '''
    video_file_path = os.path.join(input_folder, file_name)
    base_name = os.path.splitext(file_name)[0]
        
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Initialize video capture
    cap = cv2.VideoCapture(video_file_path)
    frame_count = 0
    
    # Loop through the video frames and save each frame as an image
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame_filename = os.path.join(output_folder, f"{base_name}_frame_{frame_count:04d}.png")
        cv2.imwrite(frame_filename, frame)
        frame_count += 1
    
    # Release the video capture object
    cap.release()
    print(f"Extracted {frame_count} frames to {output_folder}")
    
def get_resolution(file_name, input_folder):
    '''
    Get the resolution of a video file.
    '''
    video_path = os.path.join(input_folder, file_name)
    cap = cv2.VideoCapture(video_path)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()
    return width, height

def get_duration(file_name, input_folder):
    '''
    Get the duration of a video file.
    '''
    video_path = os.path.join(input_folder, file_name)
    cap = cv2.VideoCapture(video_path)
    duration = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS))
    cap.release()
    return duration

def create_video(images, width, height, output_path, fps=20):
    '''
    Create a video from a list of images.
    '''
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    for img in images:
        out.write(img)

    out.release()