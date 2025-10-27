import os
import shutil

def get_video_files(directory):
    '''
    Get a list of video files in a directory.
    '''
    video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.mpg']
    video_files = []

    for filename in os.listdir(directory):
        if os.path.splitext(filename)[1].lower() in video_extensions:
            video_files.append(filename)

    return video_files

def file_contains_name(file_path, test_names: list):

    return any(test_name in os.path.basename(file_path) for test_name in test_names)

def get_image_files(directory):
    '''
    Get a list of image files in a directory.
    '''
    file_ext = ('.png', '.jpg', '.jpeg', '.gif', '.bmp')
    image_files = []
    for file in os.listdir(directory):
        if os.path.splitext(file)[1].lower() in file_ext:
            image_files.append(os.path.join(directory, file))
    return image_files

def get_annotation_files(directory):
    '''
    Get a list of annotation files in a directory.
    '''
    file_ext = ('.xml', '.json', '.txt')
    annotation_files = []
    for file in os.listdir(directory):
        if os.path.splitext(file)[1].lower() in file_ext:
            annotation_files.append(os.path.join(directory, file))
    return annotation_files

def get_3d_model_files(directory):
    '''
    Get a list of 3D model files in a directory.
    '''
    file_ext = ('.obj', '.fbx', '.stl')
    model_files = []
    for file in os.listdir(directory):
        if os.path.splitext(file)[1].lower() in file_ext:
            model_files.append(os.path.join(directory, file))
    return model_files

def copy_to_staging(df, stage='train'):
    '''
    Copy files listed in the dataframe to the staging directory.
    '''
    for idx, row in df.iterrows():
        src_image_path = row['img_path']
        src_label_path = row['ann_path']
        
        # Define destination paths
        dest_image_path = os.path.join('data', 'staging', stage, os.path.basename(src_image_path))
        dest_label_path = os.path.join('data', 'staging', stage, os.path.basename(src_label_path))

        # Copy image and label files to staging directory
        shutil.copy(src_image_path, dest_image_path)
        shutil.copy(src_label_path, dest_label_path)
        
def cleanup_staging():
    '''
    Delete all files in the staging directories.
    '''
    staging_dirs = [os.path.join('data', 'staging', 'train'), os.path.join('data', 'staging', 'val')]
    for staging_dir in staging_dirs:
        for filename in os.listdir(staging_dir):
            file_path = os.path.join(staging_dir, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f'Failed to delete {file_path}. Reason: {e}')