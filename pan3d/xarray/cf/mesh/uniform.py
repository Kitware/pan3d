from vtkmodules.vtkCommonDataModel import vtkImageData


def generate_mesh(metadata, dimensions, time_index):
    data_location = "cell_data"

    # data to capture
    origin = [0, 0, 0]
    spacing = [1, 1, 1]
    extent = [0, 0, 0, 0, 0, 0]

    # extract information from dimensions
    for idx in range(len(dimensions)):
        array = metadata.xr_dataset[dimensions[-(1 + idx)]]
        # Fill in reverse order (t, z, y, x) => [0, x.size, 0, y.size, 0, z.size]
        # Use size as end of extent as we are adding 1 point for map data on cell
        extent[idx * 2 + 1] = array.size

        # axis origin/spacing
        axis_spacing = (array[-1].values - array[0].values) / (array.size - 1)
        axis_origin = float(array[0].values) - axis_spacing * 0.5

        # update global origin/spacing
        origin[idx] = axis_origin
        spacing[idx] = axis_spacing

    # Configure mesh
    mesh = vtkImageData(origin=origin, spacing=spacing, extent=extent)

    return mesh, data_location
