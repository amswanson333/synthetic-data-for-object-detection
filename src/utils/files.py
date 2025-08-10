import os

def get_video_files(directory):

    video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.mpg',
                        '.MP4', '.AVI', '.MOV', '.MKV', '.MPG']
    video_files = []

    for filename in os.listdir(directory):
        if os.path.splitext(filename)[1] in video_extensions:
            name = os.path.splitext(filename)[0]
            video_files.append(name)
            
    return video_files