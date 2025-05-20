# Configuration Files

## Introduction

Pan3D uses JSON files to save an application state for reuse. The XArray Viewer
and the Pan3D Dataset builder enable import and export features to quickly get
back to the data or state you've left off. This documentation provides
guidelines for reading and writing these files manually.

There are two sections dedicated to configure the data access and VTK mesh
extraction while the two remaining are specific for the viewer and rendering
setup. The core and mandatory part is the `data_origin` section which provide
information on where the data is located. Then we have the `dataset_config`
which capture the pieces we want to load from the XArray dataset to produce a
VTK mesh. The `preview` section is to configure the default viewer in term of
color and scaling. Finally the `camera` gather any specific camera location so
you can see the exact same thing as when you saved a given state. All of those
sections are optional except the `data_origin` and `dataset_config` is the
generated mesh is important to you.

## Example

```
{
    "data_origin": {
        "source": "url",
        "id": "https://ncsa.osn.xsede.org/Pangeo/pangeo-forge/noaa-coastwatch-geopolar-sst-feedstock/noaa-coastwatch-geopolar-sst.zarr",
        "order": "C"
    },
    "dataset_config": {
        "x": "lon",
        "y": "lat",
        "t": "time",
        "arrays": [
            "analysed_sst"
        ],
        "t_index": 5,
        "slices": {
            "lon": [1000, 6000, 20],
            "lat": [500, 3000, 20]
        }
    },
    "preview": {
        "color_by": "analysed_sst",
        "color_preset": "Cool to Warm",
        "color_min": 271.1499938964844,
        "color_max": 307.25,
        "scale_x": 1,
        "scale_y": 1,
        "scale_z": 1
    }
}
```

For more example configuration files, visit our
[Examples on Github](https://github.com/Kitware/pan3d/tree/main/examples).

## `data_origin` (Required)

The value for this key is a dictionary that should adhere to the following
schema.

| Key      | Required? | Type  | Value Description                                                                                                                  |
| -------- | --------- | ----- | ---------------------------------------------------------------------------------------------------------------------------------- |
| `source` | YES       | `str` | A string specifying a module to interpret the value for `id`. Options include "file", "url", "xarray", "pangeo", "esgf".           |
| `id`     | YES       | `str` | A unique identifier of the target dataset. Depending on the value for `source`, this may be a path, url, name, or other unique id. |
| `order`  | NO        | `str` | Specify the order convention which can either be `F` (Fortran) or `C`. The default is `C`                                          |

## `dataset_config` (Optional)

The value for this key should be a mapping specifying how to interpret the
information in the target dataset. The following table describes keys available
in this mapping schema.

| Key       | Required?         | Type        | Value Description                                                                                                                                                                                                                                           |
| --------- | ----------------- | ----------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `x`       | NO (default=None) | `str`       | The world coordinate value along X describing the grid/mesh. This should be the name of a coordinate that exists in the data array.                                                                                                                         |
| `y`       | NO (default=None) | `str`       | The world coordinate value along Y describing the grid/mesh. This should be the name of a coordinate that exists in the data array.                                                                                                                         |
| `z`       | NO (default=None) | `str`       | The world coordinate value along Z describing the grid/mesh. This should be the name of a coordinate that exists in the data array.                                                                                                                         |
| `t`       | NO (default=None) | `str`       | The coordinate name that represents slices of data, which may be time. Unlike other axes, this axis can only show one index at a time. This should be the name of a coordinate that exists in the data array.                                               |
| `t_index` | NO (default=0)    | `int`       | The index of the current time slice. Must be an integer >= 0 and < the length of the current time coordinate.                                                                                                                                               |
| `arrays`  | NO (default=[])   | `list[str]` | The set of array names we want the output mesh to contains.                                                                                                                                                                                                 |
| `slices`  | NO (default={})   | `dict`      | The set of slices and indexes performing a selection on the XArray dataset. It is a dictionary where keys are to the various coordinates array that we want to filter and the values can either define a slice (`[start, stop, step]`) or an index (`int`). |

**Slice explained:**

- `start`: the index at which the sliced data should start (inclusive)
- `stop`: the index at which the sliced data should stop (exclusive)
- `step`: an integer > 0 which represents the number of items to skip when
  slicing the data (e.g. step=2 represents 0.5 resolution)

## `preview` (Optional)

This section is only relevant when using the default XArray Viewer from Pan3D.
It capture what to display and how. The following table describes keys available
in this mapping schema.

| Key            | Required?                   | Type    | Value Description                                                                                                                                     |
| -------------- | --------------------------- | ------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| `view_3d`      | NO (default=True)           | `bool`  | If true, the 3D interaction will rotate the dataset. Otherwise, a 2D interaction will be used (pan instead of rotate) along with parallel projection. |
| `color_by`     | NO (default=None)           | `str`   | Name of a loaded array that we want to display.                                                                                                       |
| `color_preset` | NO (default='Cool to Warm') | `str`   | Name of a color preset for scalar mapping.                                                                                                            |
| `color_min`    | NO (default=None)           | `float` | Scalar value that will be mapped to the lower end of the color scale.                                                                                 |
| `color_max`    | NO (default=None)           | `float` | Scalar value that will be mapped to the upper end of the color scale.                                                                                 |
| `scale_x`      | NO (default=`1`)            | `float` | Rendering scale to apply on the X axis.                                                                                                               |
| `scale_y`      | NO (default=`1`)            | `float` | Rendering scale to apply on the Y axis.                                                                                                               |
| `scale_z`      | NO (default=`1`)            | `float` | Rendering scale to apply on the Z axis.                                                                                                               |

## `camera` (Optional)

The value for this key configure the VTK camera for any specific viewer or
explorer.

| Key                   | Required?         | Type          | Value Description                                                                    |
| --------------------- | ----------------- | ------------- | ------------------------------------------------------------------------------------ |
| `position`            | NO (default=None) | `list[float]` | 3D Coordinate of the camera position.                                                |
| `view_up`             | NO (default=None) | `list[float]` | Vector defining the vertival axis.                                                   |
| `focal_point`         | NO (default=None) | `list[float]` | 3D Coordinate of where the camera is looking at.                                     |
| `parallel_projection` | NO (default=0)    | `int`         | Either 1 or 0 to define if the camera should use perspective or parallel projection. |
| `parallel_scale`      | NO (default=None) | `float`       | Zooming factor when `parallel_projection=1`.                                         |
