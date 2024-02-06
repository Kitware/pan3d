# Dataset Viewer Tutorial

## Introduction

Pan3D aids data scientists in exploring multidimensional datasets. For this tutorial, we will refer to a public multidimensional dataset provided by Pangeo Forge. This dataset was collected by the Copernicus Climate Change Service (C3S) as part of the **E**urope **OBS**ervational (E-OBS) gridded dataset. It contains observational data for precipitation, temperature, humidity, and air pressure.

For more information about this dataset, visit [the C3S Catalog](https://surfobs.climate.copernicus.eu/surfobs.php).

## Get started

To follow along this tutorial, install Pan3D.

```
pip install pan3d
```

Run the viewer as a local python server with the following command.

```
pan3d-viewer --dataset=https://ncsa.osn.xsede.org/Pangeo/pangeo-forge/pangeo-forge/EOBS-feedstock/eobs-tg-tn-tx-rr-hu-pp.zarr
```

The Pan3D Viewer will open as a tab in your default browser. You can also visit `localhost:8080` in another browser.

 > **Note:** to prevent the behavior of opening a tab on startup, add `--server` to the above command to run server mode.

## Using the Viewer

#### Data configuration

After a moment to load the data from the remote URL, the Viewer will render the default configuration of the target dataset.

![](../images/1.png)


You can open the left drawer by clicking on the dataset configuration icon in the top left.

![](../images/2.png)

Inside this panel, you will find the following information:

- A dataset selection box. Its current value is the url we passed as an argument. There are more datasets available in the dropdown; these are examples from Xarray.
- A button to view the attributes of the current dataset. Click the three-dots icon next to "Attributes" to open a dialog table of metadata available on the dataset.

    ![](../images/3.png)

- A list of arrays available in the dataset, each with a button to view its attributes. The arrays in this dataset are acronymns, so we can open the attributes tables to see the standard names. The first array is mean relative humidity, and we can see the unit is a percentage.

    ![](../images/4.png)

You can select any array from this list by clicking on the name. For this tutorial, we will continue with the the mean temperature data in the array called "tg".

When a new data array is selected, the axis drawer on the right will open for further data configuration. This drawer allows us to change the default axis assignments and slicing. This drawer can be toggled with the axis info icon in the top right corner.

By default, "longitude" is assigned to X, "latitude" is assigned to Y, and "time" is assigned to T. This data does not have a Z coordinate, so our rendered meshes are all planes. We will explore a 3D dataset later.

![](../images/5.png)

We can expand any of these coordinate panels. When we expand longitude, we see the following information

- The attributes table of the coordinate. For longitude, the units are degrees east, and there are 705 values ranging from -24.95 to 45.45.

- Inputs to adjust the slicing along the coordinate. For longitude, the default slicing starts at -24.95, stops at 45.45, and has a step of 1. This includes all values in the coordinate array.

- A selection box to assign the coordinate to an axis. These coordinates have already been assigned to each axis automatically.

![](../images/6.png)

> **Note:** Each time you change a value in this panel, Pan3D will attempt to make a new render. If you plan on making many changes before you want to re-render, disable the Auto Render feature with the checkbox in the top right. A button will appear when you have made changes that have not been applied. You can click this button to trigger the re-render once you have made all changes. The button displays the total size of the data that will be loaded for the render.

> ![](../images/6a.png)

We can crop the rendered mesh and reduce its resolution by adjusting the slicing along these coordinates. After setting the start longitude to 0 and setting the step along longitude to 5, we get the following rendering.

![](../images/7.png)


We'll put our slicing back to how it was so we can see the full image again. Then, we'll expand the time coordinate and see that the panel is slightly different.

Instead of slicing options, the time coordinate has a slider. We can only look at one slice at a time. Take note that this time axis has 25933 slices. Pan3D will only load the data for the current slice, so we don't load data that we don't need to render. This means that each time we change the slice, Pan3D will need to fetch more data, but each fetch will be much faster than trying to load the whole dataset at once.

By default, we start on the first slice, with index 0, which corresponds to January 01, 1950 at midnight. We can see from the attributes table that the time coordinate range begins with this time and ends with December 31, 2020.

You can pick any index along this slider, and the label above will tell you what time that index corresponds to. Below, we have gone forward in time to June 25, 2004, and Europe appears much warmer.

![](../images/8.png)

#### Render configuration

Let's close the data configuration drawers and focus on the rendering area. There are many options to customize the appearance of the rendering within this space.

1. We can move the camera around the rendered mesh by clicking and dragging. We can pan the camera by holding Shift while dragging, and we can rotate it by holding Ctrl while dragging. We can move the camera toward the mesh and away from it by scrolling. We can see this mesh is a plane. We'll look at a 3D dataset soon.

2. The color legend is interactive. We can drag it to another edge of the scene, or we can resize it by using the white bounding bars that appear when we click on the legend.

    ![](../images/9.png)

3. The circle with the three-dots icon in the top left opens a Views menu. Beside the three-dots icon, there are 12 buttons for you to try.

    ![](../images/9a.png)

    This menu contains the following options:

    1. A button to reset the camera position and re-center the mesh.
    2. A button to set the camera in a perspective view.
    3. A button to put the camera on the X axis (our plane will be invisible from this view).
    4. A button to put the camera on the Y axis (our plane will be invisible from this view).
    5. A button to put the camera on the Z axis (this is the default view for our plane).
    6. A button to toggle edge visibility (with our current high resolution, there are a lot of edges. Try zooming in when you enable this).
    7. A button to toggle bounding box visibility (this will draw a thin border around our plane when enabled).
    8. A button to toggle ruler visibility (these will show our latitude and longitude scales).
    9. A button to toggle an axis widget's visibility (this will appear in the bottom left. Try rotating the scene while this is enabled).
    10. A button to toggle between local and remote rendering mode. Local rendering is the default and is recommended for basic use cases.
    11. A button to save the current visual as a static PNG file.
    12. A button to save the current rendering as an interactive HTML scene.

4. The circle with the gear icon in the top right opens a rendering customization menu. This menu contains four customization options.

    ![](../images/9b.png)

    1. A colormap selection box. The default is "viridis". These options come from Matplotlib.
    2. A checkbox to enable transparency. When enabled, another selection box will appear with options for transparency function. The default is "linear".
    3. A checkbox to enable scalar warping. When enabled, scalar warping turns the rendered flat plane into a 3D mesh, where values are extruded in the Z axis according to their magnitudes.
    4. Inputs to specify the relative scales of each axis. By default, this is a 1:1:1 ratio.

By using these configuration options, we can get a rendering like the one shown below. For this rendering, we did the following:

- moved the color legend
- changed the colormap to "plasma"
- enabled transparency and changed the transparency function to "linear_r" (which means reverse linear)
- enabled scalar warping
- changed the axis scale ratio to 2:2:1 so the scalar warping would be less extreme
- enabled ruler visibility
- reset the camera to perspective view

![](../images/10.png)

Take a moment to try out different combinations to see how else this data can be configured to appear.

#### Saving configurations

The Pan3D viewer is intended to allow scientists to explore a dataset to find ideal visualizations with these many configuration options. Once you have found a visualization you like, you can use the PNG and HTML export options in the Views menu, but you can also export this configuration for fast replication within Pan3D.

After we finish our configuration and have a finalized rendering, we can click the "Export" button in the top toolbar. Clicking this button will open a dialog, which asks for a location to save a configuration file.

![](../images/11.png)

Some browsers, like Chrome, will allow specification of a download folder when you click on this input. Other browsers, like Firefox, do not allow this feature and will save the file to your default Downloads folder. By default, this file will be called `pan3d_state.json`. In browsers where you can specify download location, you can also change this name.

Once you have specified a download location, a file will be saved to your computer and the dialog will change.

![](../images/11a.png)

For our configuration, the contents of the exported file appear as follows:

```
{
    "data_origin": "https://ncsa.osn.xsede.org/Pangeo/pangeo-forge/pangeo-forge/EOBS-feedstock/eobs-tg-tn-tx-rr-hu-pp.zarr",
    "data_array": {
        "name": "tg",
        "x": "longitude",
        "y": "latitude",
        "t": "time",
        "t_index": 19899
    },
    "data_slices": {
        "time": [
            "Jan 01 1950 00:00",
            "Dec 31 2020 00:00",
            1
        ],
        "latitude": [
            25.05,
            71.45,
            2
        ],
        "longitude": [
            -24.95,
            45.45,
            2
        ]
    },
    "ui": {
        "loading": false,
        "main_drawer": false,
        "axis_drawer": false,
        "unapplied_changes": false,
        "error_message": null,
        "more_info_link": null,
        "expanded_coordinates": [],
        "current_time_string": "Jun 25 2004 00:00"
    },
    "render": {
        "auto": false,
        "x_scale": 2,
        "y_scale": 2,
        "z_scale": 1,
        "scalar_warp": true,
        "transparency": true,
        "transparency_function": "linear_r",
        "colormap": "plasma"
    }
}
```

To learn more about the schema to which this configuration file adheres, visit the [Configuration Files documentation](../api/configuration.md).

Now, a collaborator can easily replicate our rendering. Try to save the JSON contents above to a file on your computer and follow along as if you just received this file from a colleague.

Clicking the "Import" button in the top toolbar will open a similar dialog. Click the file input to select the location of the configuration file on your computer.

![](../images/12.png)

Once the file has been selected, another "Import" button will appear. After clicking this button, the dialog will change and Pan3D will begin loading the configuration and applying the changes.

![](../images/12a.png)

After a moment to load, Pan3D will render the replicated scene.

These configuration files can be used as arguments in the local server startup command (see [Local Python Server tutorial](./local_server.md) for details) or can be used in a Jupyter notebook environment (see [Jupyter Notebook tutorial](./jupyter_notebook.md) for details).

#### Viewing other data

Open the left drawer again and look at the list of datasets available in the dataset selection dropdown. You can look at any of these examples from Xarray and try out the configuration options we have reviewed.

There is one dataset among these with 4D data, which means we can select a time slice and get a 3D render. Select "Xarray Examples - ERA-Interim analysis" to experiment with these options on a 3D mesh.

![](../images/13.png)

This concludes the tutorial on how to use the Pan3D viewer.
