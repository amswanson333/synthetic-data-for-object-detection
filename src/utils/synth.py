import vtk
from vtk.util import numpy_support
from PIL import Image
from PIL import ImageFilter
import numpy as np
from google import genai
import os
import io


# Load a 3D model from a file into a VTK PolyData object
def load_3d_model(file_path):
    # Create a VTK reader based on the file extension
    file_ext = os.path.splitext(file_path)[1].lower()
    if file_ext == '.obj':
        reader = vtk.vtkOBJReader()
    elif file_ext == '.fbx':
        reader = vtk.vtkFBXReader()
    elif file_ext == '.stl':
        reader = vtk.vtkSTLReader()
    else:
        raise ValueError(f"Unsupported file format: {file_ext}")

    # Set the file name and update the reader
    reader.SetFileName(file_path)
    reader.Update()

    # Return the PolyData object
    return reader.GetOutput()

# Create a view of the 3D model using VTK
def view_model(model_data):
    # Create a VTK renderer, render window, and interactor
    renderer = vtk.vtkRenderer()
    render_window = vtk.vtkRenderWindow()
    render_window.AddRenderer(renderer)
    render_window_interactor = vtk.vtkRenderWindowInteractor()
    render_window_interactor.SetRenderWindow(render_window)

    # Create a mapper and actor for the model
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputData(model_data)
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)

    # Add the actor to the renderer
    renderer.AddActor(actor)
    renderer.SetBackground(0.1, 0.1, 0.1)  # Set background color

    # Start the rendering loop
    render_window.Render()
    render_window_interactor.Start()
    
# Create a VTK camera view of the model
def camera_view(model_data, distance=2000, init_pitch=0, init_yaw=-90, init_roll=0, randomize=False, seed=0):
    
    rng = np.random.default_rng(seed)
    
    # Create a VTK renderer, render window, and interactor
    renderer = vtk.vtkRenderer()
    renderer.SetBackground(0, 0, 0)  # Black, but will be transparent
    renderer.SetBackgroundAlpha(0)   # Set alpha to 0 for transparency

    render_window = vtk.vtkRenderWindow()
    render_window.SetAlphaBitPlanes(1)  # Enable alpha bit planes
    render_window.AddRenderer(renderer)
    render_window_interactor = vtk.vtkRenderWindowInteractor()
    render_window_interactor.SetRenderWindow(render_window)

    # Create a mapper and actor for the model
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputData(model_data)
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    
    # Apply color to the model
    actor.GetProperty().SetColor(0.5, 0.5, 0.5)
    
    # Randomize color of model if randomize is True
    if randomize:
        actor.GetProperty().SetColor(rng.uniform(0.1, 0.9), rng.uniform(0.1, 0.9), rng.uniform(0.1, 0.9))
    
    # Initial orientation of the actor (model)
    # Initial orientation is designed to initialize model facing to the right
    pitch_degrees = init_pitch
    yaw_degrees = init_yaw
    roll_degrees = init_roll
    actor.RotateX(pitch_degrees)
    actor.RotateZ(yaw_degrees)
    actor.RotateY(roll_degrees)
    
    # Add some random rotation to the model
    if randomize:
        actor.RotateX(rng.uniform(-90, 90))  # Random pitch adjustment
        actor.RotateZ(rng.uniform(-180, 180))  # Random yaw adjustment
        actor.RotateY(rng.uniform(-45, 45))  # Random roll adjustment

    # Add the actor to the renderer
    renderer.AddActor(actor)

    # Set up the camera
    camera = vtk.vtkCamera()
    camera.SetPosition(0, distance, 0)
    camera.SetFocalPoint(0, 0, 0)
    camera.SetViewUp(0, 0, -1)
    camera.SetClippingRange(1, 10000)
    renderer.SetActiveCamera(camera)

    # Save the camera view as an image
    camera.SetParallelProjection(1)  # Use parallel projection for orthographic view
    camera.SetParallelScale(1000)    # Adjust the scale for better visibility
    renderer.ResetCamera()
    render_window.SetSize(1600, 1200)  # Set the window size
    render_window.Render()

    # Create a PNG writer to save the image
    windowToImageFilter = vtk.vtkWindowToImageFilter()
    windowToImageFilter.SetInput(render_window)
    windowToImageFilter.SetInputBufferTypeToRGBA()  # Enable RGBA for transparency
    windowToImageFilter.ReadFrontBufferOff()
    windowToImageFilter.Update()

    png_writer = vtk.vtkPNGWriter()
    png_writer.SetWriteToMemory(1)
    png_writer.SetInputConnection(windowToImageFilter.GetOutputPort())
    png_writer.Write()
    
    # Create output in bytes object
    output_result = png_writer.GetResult()
    mem_view = memoryview(output_result)
    output_raw = bytes(mem_view)
    
    return output_raw

def vtk_to_PIL(camera_view):
    
    img = Image.open(io.BytesIO(camera_view))
    
    image_box = img.getbbox()
    img = img.crop(image_box)
    
    return img

def rng_scale(seed=0):
    rng = np.random.default_rng(seed)
    base = rng.gamma(shape=4.5, scale=0.08)
    return 0.002 + (base / 8)

def rng_position(obj_size=(1, 1), canvas_size=(640, 480), seed=0):
    rng = np.random.default_rng(seed)
    
    # Get random values for x and y position from normal distribution
    samples = rng.normal(size=2)
    
    # Set the values to between 0 and 1 using a sigmoid function
    x_pos = 1 / (1 + np.exp(-samples[0]))
    y_pos = 1 / (1 + np.exp(-samples[1]))
    
    # Adjust absolute x,y position to pixel position
    # NOTE: this prevents the image from overlapping any edge
    x_pos = x_pos * (canvas_size[0] - obj_size[0])
    y_pos = y_pos * (canvas_size[1] - obj_size[1])
    
    return (int(x_pos), int(y_pos))

def scale_obj(obj_image, scale, canvas_size=(640, 480)):
    obj_width, obj_height = obj_image.size
    aspect_ratio = obj_width / obj_height
    
    new_width = int(scale * canvas_size[0])
    new_height = int(new_width / aspect_ratio)
    
    resized_obj = obj_image.resize((new_width, new_height), Image.BICUBIC)
    
    return resized_obj

def rng_transform(obj_image, seed=42):
    rng = np.random.default_rng(seed)
    
    # Randomly select a transformation
    rand_int = rng.integers(low=0, high=8)
    
    # Default no transform
    if rand_int == 0:
        return obj_image
    # Flip image left-right
    if rand_int == 1:
        return obj_image.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    # Flip image up-down
    if rand_int == 2:
        return obj_image.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
    # Apply gaussian blur
    if rand_int == 3:
        return obj_image.filter(ImageFilter.GaussianBlur(2))
    # Apply smoothing
    if rand_int == 4:
        return obj_image.filter(ImageFilter.SMOOTH)
    # Change hue
    if rand_int == 5:
        hsv_obj = obj_image.convert("HSV")
        h, s, v = hsv_obj.split()
        
        h = h.point(lambda i: i * rng.uniform(0.15, 0.85))
        
        result_img = Image.merge("HSV", (h, s, v)).convert("RGB")
        
        return result_img
    # Change saturation
    if rand_int == 6:
        hsv_obj = obj_image.convert("HSV")
        h, s, v = hsv_obj.split()
        
        s = s.point(lambda i: i * rng.uniform(0.15, 0.85))
        
        result_img = Image.merge("HSV", (h, s, v)).convert("RGB")
        
        return result_img
    # Change value
    if rand_int == 7:
        hsv_obj = obj_image.convert("HSV")
        h, s, v = hsv_obj.split()
        
        v = v.point(lambda i: i * rng.uniform(0.15, 0.85))
        
        result_img = Image.merge("HSV", (h, s, v)).convert("RGB")
        
        return result_img

def canvas_prompt(terrain, time_of_day, condition, season, seed=0):
    rng = np.random.default_rng(seed)
    
    terrain = rng.choice(terrain)
    time_of_day = rng.choice(time_of_day)
    condition = rng.choice(condition)
    season = rng.choice(season)

    prompt = f"A photo of {terrain} landscape in {season} at {time_of_day} with {condition} weather taken by a professional photographer."
        
    return prompt

def canvas_genai(client, prompt, number_of_images):
    
    model = "imagen-3.0-generate-002"
    
    gen_config = genai.types.GenerateImagesConfig(
        number_of_images=number_of_images,
        aspect_ratio="16:9"
    )
    
    response = client.models.generate_images(
        model = model,
        prompt = prompt,
        config = gen_config
    )
    
    return response.generated_images

def object_prompt(object_types, object_colors, maneuvers, seed=0):
    rng = np.random.default_rng(seed)
    
    object_type = rng.choice(object_types)
    color = rng.choice(object_colors)
    maneuver = rng.choice(maneuvers)

    prompt = f"A photo of a single, {color} colored {object_type} drone {maneuver} through the air against a seamless, solid green background."
        
    return prompt

def object_genai(client, prompt, number_of_images):
    
    model = "imagen-3.0-generate-002"
    
    gen_config = genai.types.GenerateImagesConfig(
        number_of_images=number_of_images,
        aspect_ratio="4:3"
    )
    
    response = client.models.generate_images(
        model = model,
        prompt = prompt,
        config = gen_config
    )
    
    return response.generated_images

def object_mask(obj_image):    
    # Convert image channels to numpy arrays
    red_arr = np.array(obj_image.split()[0])
    green_arr = np.array(obj_image.split()[1])
    blue_arr = np.array(obj_image.split()[2])
    
    # Create a blank binary mask
    mask = np.zeros(green_arr.shape, dtype=np.uint8)
    
    # If the brightest channel is green, set mask pixel to 255 (white)
    mask[(green_arr > red_arr) & (green_arr > blue_arr)] = 255
    
    # Convert numpy array back to PIL image
    binary_mask = Image.fromarray(mask)

    return binary_mask

def object_alpha(obj_image, obj_mask):
    # Ensure both images are in RGBA mode
    obj_image = obj_image.convert("RGBA")
    obj_mask = obj_mask.convert("L")  # Convert mask to grayscale

    # Create a new image for output
    output_image = Image.new("RGBA", obj_image.size)

    # Get pixel data
    obj_pixels = obj_image.load()
    mask_pixels = obj_mask.load()
    output_pixels = output_image.load()

    # Apply the mask to the object image
    for y in range(obj_image.height):
        for x in range(obj_image.width):
            r, g, b, a = obj_pixels[x, y]
            mask_value = mask_pixels[x, y]
            if mask_value == 255:
                output_pixels[x, y] = (r, g, b, 255)  # Keep original pixel with full opacity
            else:
                output_pixels[x, y] = (0, 0, 0, 0)      # Set pixel to transparent

    return output_image

def object_crop(obj_image):
    # Get bounding box of non-transparent pixels
    bbox = obj_image.getbbox()
    
    # Crop the image to the bounding box
    cropped_image = obj_image.crop(bbox)
    
    return cropped_image