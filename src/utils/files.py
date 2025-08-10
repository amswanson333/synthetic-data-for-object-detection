import os

def get_video_files(directory):

    video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.mpg']
    video_files = []

    for filename in os.listdir(directory):
        if os.path.splitext(filename)[1].lower() in video_extensions:
            video_files.append(filename)

    return video_files