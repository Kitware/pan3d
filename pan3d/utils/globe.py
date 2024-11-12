import os
import vtk
import numpy as np
from vtkmodules.numpy_interface import dataset_adapter as dsa
from vtkmodules.util import numpy_support

from pan3d.explorers.filters import EAMSphere


def get_globe():
    # Add globe underlayment
    # Define grid dimensions (size in each direction)
    grid_dimensions = [361, 181, 1]  # 10x10x10 grid
    uniform_grid = vtk.vtkUniformGrid()
    uniform_grid.SetDimensions(grid_dimensions)
    uniform_grid.SetSpacing(1.0, 1.0, 0.0)
    uniform_grid.SetOrigin(-180.0, -90.0, 0.0)

    append = vtk.vtkAppendDataSets()
    append.AddInputData(uniform_grid)
    append.Update()

    grid = append.GetOutput()

    grid_np = dsa.WrapDataObject(grid)
    points = np.array(grid_np.Points)
    x = points[:, 0]  # x-coordinate
    y = points[:, 1]  # y-coordinate
    # Map data's longitude (0 to 360) to texture's longitude (-180 to 180)
    x_texture = x - 180  # Convert longitude data to texture's longitude range
    # Normalize the texture coordinates: Longitude (-180 to 180) -> u (0 to 1)
    u = (x_texture) / 360.0
    v = (y + 90.0) / 180.0
    texture_coords_np = np.vstack((u, v)).T
    texture_coords = numpy_support.numpy_to_vtk(texture_coords_np)
    grid.GetPointData().SetTCoords(texture_coords)

    globe = EAMSphere()
    globe.input_data_object = grid
    # Need explicit geometry extraction when used with WASM
    geometry = vtk.vtkDataSetSurfaceFilter(input_connection=globe.output_port)
    geometry.Update()
    return geometry.output


def get_globe_texture():
    sep = os.path.sep
    datadir = os.path.dirname(os.path.realpath(__file__)) + sep + "data"

    # Load a texture (JPEG image in this case)
    jpeg_reader = vtk.vtkJPEGReader()
    jpeg_reader.SetFileName(datadir + sep + "world.topo.bathy.200408.3x5400x2700.jpg")
    jpeg_reader.Update()

    # Create a vtkTexture object
    texture = vtk.vtkTexture()
    texture.SetInputConnection(jpeg_reader.GetOutputPort())
    texture.InterpolateOn()

    return texture


def get_continent_outlines():
    sep = os.path.sep
    datadir = os.path.dirname(os.path.realpath(__file__)) + sep + "data"

    vtk_reader = vtk.vtkDataSetReader()
    vtk_reader.SetFileName(datadir + sep + "continents.vtk")
    vtk_reader.Update()
    vtk_reader.output.GetPointData().SetActiveScalars("cstar")

    contour = vtk.vtkContourFilter()
    contour.input_data_object = vtk_reader.output
    contour.SetValue(0, 0.5)
    contour.SetNumberOfContours(1)
    contour.Update()

    continents = EAMSphere()
    continents.input_data_object = contour.output
    continents.Update()
    # Need explicit geometry extraction when used with WASM
    geometry = vtk.vtkDataSetSurfaceFilter(input_connection=continents.output_port)
    geometry.Update()

    return geometry.output
