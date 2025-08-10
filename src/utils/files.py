import os

def get_video_files(directory):

    video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.mpg']
    video_files = []

    for filename in os.listdir(directory):
        if os.path.splitext(filename)[1].lower() in video_extensions:
            name = os.path.splitext(filename)[0]
            video_files.append(name)
            
    return video_files