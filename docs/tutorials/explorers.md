# Pan3D Explorers Tutorial

## Introduction

Pan3D provides four specialized visualization tools called Explorers, each
designed for specific data exploration tasks. These focused tools offer clean,
intuitive interfaces tailored to their purpose, avoiding the complexity of
general-purpose visualization software.

## Getting Started

Install Pan3D with viewer capabilities:

```bash
pip install "pan3d[viewer]"
```

Each explorer can be launched from the command line with optional data sources:

```bash
# Launch with interactive data selection
xr-slicer
xr-globe
xr-contour
xr-analytics

# Launch with specific data
xr-slicer --xarray-file ./data.nc
xr-globe --xarray-url https://example.com/data.zarr
xr-contour --import-state ./config.json
```

## Slice Explorer

**Purpose**: Navigate through 3D volumes by extracting 2D slices along any axis.

**Best for**: Atmospheric data, medical imaging, geological surveys, or any
volumetric dataset requiring cross-sectional analysis.

![Slice Explorer](../images/SliceExplorer.png)

**Key Features:**

- **Axis Slicing**: Extract 2D slices along X, Y, or Z axes
- **View Modes**: 2D orthogonal or 3D perspective visualization
- **Volume Context**: Display outline and apply transparency to 3D data
- **Dynamic Updates**: Real-time slice rendering as position changes

**Example Use Case**: Explore temperature layers in atmospheric data by slicing
along altitude to understand thermal stratification.

**Launch Command**: `xr-slicer`

## Globe Explorer

**Purpose**: Visualize geographic data on a realistic 3D Earth with accurate
projection.

**Best for**: Climate data, oceanographic measurements, satellite observations,
or any dataset with latitude/longitude coordinates.

![Globe Explorer](../images/GlobeExplorer.png)

**Key Features:**

- **Texture Options**: Satellite imagery, topography, political boundaries
- **Continental Outlines**: Overlay continent boundaries on data
- **Terrain Elevation**: Apply bump mapping for topographic effects
- **Sphere Projection**: Map latitude/longitude data to 3D globe

**Example Use Case**: Visualize global temperature anomalies with continental
context to identify regional climate patterns.

**Launch Command**: `xr-globe`

## Contour Explorer

**Purpose**: Create smooth contour visualizations with color-banded regions
between isolevels.

**Best for**: Scalar fields, topographic data, gradient analysis, or any dataset
requiring isoline visualization.

![Contour Explorer](../images/ContourExplorer.png)

**Key Features:**

- **Banded Regions**: Generate filled areas between contour levels
- **Contour Lines**: Overlay black isolines on banded regions
- **Level Control**: Set number and range of contour values
- **Surface Smoothing**: Apply loop subdivision for refined contours

**Example Use Case**: Analyze ocean temperature at specific depths to identify
thermoclines and current patterns.

**Launch Command**: `xr-contour`

## Analytics Explorer

**Purpose**: Combine 3D visualization with statistical analysis for
comprehensive data exploration.

**Best for**: Time series analysis, spatial statistics, trend detection, or any
dataset requiring both visual and quantitative insights.

![Analytics Explorer](../images/AnalyticsExplorer.png)

**Key Features:**

- **Statistical Plots**: Zonal, temporal, and global analysis charts
- **Temporal Grouping**: Aggregate data by year, month, day, or hour
- **xCDAT Integration**: Leverage climate analysis algorithms
- **Data Synchronization**: 3D view and plots update together

**Example Use Case**: Analyze seasonal temperature patterns by combining 3D
visualization with monthly statistical plots.

**Launch Command**: `xr-analytics`

## Common Features

All explorers share these capabilities:

### Data Management

- Load from files, URLs, or configuration states
- Support for xarray-compatible formats
- State export/import for reproducibility

### Visualization Controls

![Common Controls](../images/common.png)

- **Time Navigation**: Slider, play/pause, step controls for temporal data
- **Color Mapping**: Presets, custom ranges, interactive scalar bar
- **Scale Controls**: Independent X/Y/Z scaling for different unit scales

### Performance Tips

- Use data stepping/striding for large datasets
- Crop to regions of interest
- Start with lower resolution, increase as needed

## Choosing the Right Explorer

| Explorer      | Best For                                                 |
| ------------- | -------------------------------------------------------- |
| **Slice**     | Volumetric data, internal structures, cross-sections     |
| **Globe**     | Geographic data, global patterns, Earth visualization    |
| **Contour**   | Value ranges, smooth gradients, publication figures      |
| **Analytics** | Statistical analysis, time series, quantitative insights |

## Integration Example

Use explorers in Jupyter notebooks:

```python
from pan3d.explorers.slicer import SliceExplorer

# Create and display explorer
explorer = SliceExplorer()
await explorer.ui.ready

# Launch the interactive explorer within jypyter notebook
explorer.ui

# Export configuration
config = explorer.export_state()
```

## Additional Resources

- [Configuration API Documentation](../api/configuration.md)
- [Jupyter Integration Tutorial](jupyter_notebook.md)
- [Command Line Reference](command_line.md)
