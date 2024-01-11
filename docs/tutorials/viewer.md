# How to use the Pan3D Viewer

Pan3D is intended to aid data scientists in exploring a given multidimensional dataset, so for this tutorial we will refer to a public dataset provided by Pangeo Forge. This dataset, provided by the National Oceanic and Atmospheric Administration (NOAA), maps global sea surface temperatures over time.  Visit [https://pangeo-forge.org/dashboard/feedstock/3](https://pangeo-forge.org/dashboard/feedstock/3) to view more information about this data.

1. When first launched with a target dataset, the Pan3D interface will look similar to the below screenshot. Pan3D has automatically selected the first available array in the dataset, called `analysed_sst`, and it has also automatically assigned the coordinates for this array to axes X, Y, and T, since the coordinates have standard names.

    ![](../images/1.png)

2. The left panel provides information about the dataset and its available arrays. Click any of the dots icons to view a table of attributes for the dataset or any of its arrays.

    ![](../images/2.png)

3. The right panel provides information and configuration options for how the data is assigned to each axis for rendering. You can expand any of these coordinate panels to view the coordinate attributes, change the slicing, or reassign the axis. To change the slicing of the coordinate, you can adjust the start value and stop value to crop the rendering to a region of interest. You can also increase the step value to decrease the resolution for a faster render time on large datasets. The default step of 1 represents the maximum resolution for the data.

    ![](../images/3.png)

4. As you adjust the slicing for various coordinates, the total render size will adjust accordingly. The total render size is displayed on the “Apply & Render” button. Keep in mind this will affect the rendering time. After changing the step value to 5 for latitude and longitude, we have decreased the resolution and therefore decreased the total render size from 99 MB to 4 MB. Now we click the “Apply & Render” button and it takes 10 seconds to show the following visual.

    ![](../images/4.png)

5. You can also adjust the time coordinate by selecting the index of the current time slice. When the time coordinate is expanded, you have a slider of all the available time steps in the active array. This data has over 7,000 time steps from September 01, 2002 to March 20, 2022. After changing the slider value, the date and time of the current step is shown and the “Apply & Render” button becomes enabled. To render the selected time step, the scene must be rerendered. The screenshot below shows the data on May 08, 2005.

    ![](../images/5.png)

6. You can adjust the rendering with some of the options available in the menus in the rendering area.

    The right menu, when expanded, offers options to change the rendered visual. You can change the color map, transparency, warping, and the scales of each axis. The first screenshot below shows a different color map and scalar warping enabled. The scalar warping turns the rendered flat plane into a 3D mesh, where values are extruded in the Z axis according to their magnitudes.

    The left menu, when expanded, offers camera controls, options to toggle edge visibility and bounding box visibility, a ruler widget, and an axis legend widget. It also offers buttons to export the rendered scene as a static PNG or dynamic HTML render. The second screenshot below shows enabled edge visibility. In this screenshot, the data has been sliced for a lower resolution rendering so that the edges may be seen better.

    The screenshots below also show that the color legend has been moved; the user can adjust the size and position of this legend as needed.

    ![](../images/6.png)
    ![](../images/9.png)

7. Once you have used the Pan3D viewer to configure the data for a desired render, you can export the data configuration for faster reuse and easier collaboration. The import and export buttons are available in the top toolbar.

    ![](../images/7.png)

8. You can use the exported configuration file (“pan3d_state.json” by default) with the Import dialog, or you can reference its path in the launch process to automatically start with that state. See [How to run Pan3D as a local Python server](./local_server.md) and [How to use Pan3D in a Jupyter Notebook](./jupyter_notebook.md) to see how to use these config files in the launch process.
