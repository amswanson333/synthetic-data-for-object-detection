import vtk
from vtk.util import numpy_support
from PIL import Image
import numpy as np
import os
import io

# Get the list of 3D model files
def get_3d_model_files(directory):
    file_ext = ('.obj', '.fbx', '.stl')
    model_files = []
    for file in os.listdir(directory):
        if os.path.splitext(file)[1].lower() in file_ext:
            model_files.append(os.path.join(directory, file))
    return model_files

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
def camera_view(model_data, distance=2000, init_pitch=0, init_yaw=-90, init_roll=0):
    
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
    
    # Initial orientation of the actor (model)
    # Initial orientation is designed to initialize model facing to the right
    pitch_degrees = init_pitch # Realistic orientation range [-90,90]
    yaw_degrees = init_yaw # Realistic orentation range [-180,180]
    roll_degrees = init_roll # Realistic orientation range [-180,180]
    actor.RotateX(pitch_degrees)
    actor.RotateZ(yaw_degrees)
    actor.RotateY(roll_degrees)

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