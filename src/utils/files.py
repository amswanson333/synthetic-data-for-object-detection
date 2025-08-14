import os

def get_video_files(directory):

    video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.mpg']
    video_files = []

    for filename in os.listdir(directory):
        if os.path.splitext(filename)[1].lower() in video_extensions:
            video_files.append(filename)

    return video_files

def file_contains_name(file_path, test_names: list):

    return any(test_name in os.path.basename(file_path) for test_name in test_names)
