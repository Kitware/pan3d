import warnings

import vtkmodules.vtkRenderingAnari as vtkRenderingAnari
import vtkmodules.vtkRenderingOpenGL2  # noqa: F401
from vtkmodules.vtkFiltersGeometry import vtkGeometryFilter

# VTK factory initialization
from vtkmodules.vtkInteractionStyle import vtkInteractorStyleSwitch  # noqa: F401
from vtkmodules.vtkInteractionWidgets import vtkOrientationMarkerWidget
from vtkmodules.vtkRenderingAnnotation import vtkAxesActor
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper,
    vtkRenderer,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
)

from pan3d.ui.analytics import (
    GroupBy,
    Plotting,
    PlotTypes,
    group_options,
    plot_options,
    zonal_axes,
)
from pan3d.ui.layouts import StandardExplorerLayout
from pan3d.ui.preview import RenderingSettings
from pan3d.utils.common import Explorer
from pan3d.utils.convert import to_float
from pan3d.widgets.pan3d_view import Pan3DView
from pan3d.xarray.algorithm import vtkXArrayRectilinearSource
from trame.decorators import change
from trame.widgets import html
from trame.widgets import vuetify3 as v3


class Pan3dAnalyticsView(Pan3DView):
    def __init__(self, render_window, **kwargs):
        super().__init__(render_window=render_window, **kwargs)
        with self.toolbar:
            v3.VDivider(classes="my-1")
            with v3.VTooltip(text="Display charting/plotting drawer"):
                with html.Template(v_slot_activator="{ props }"):
                    v3.VBtn(
                        v_bind="props",
                        flat=True,
                        density="compact",
                        icon="mdi-chart-line",
                        click="plot_drawer = !plot_drawer",
                    )


class AnalyticsExplorer(Explorer):
    # Define which properties are relevant for each plot type
    PLOT_PROPERTY_RELEVANCE = {
        PlotTypes.ZONAL: {"zonal_axis"},
        PlotTypes.ZONALTIME: {"zonal_axis", "group_by"},
        PlotTypes.GLOBAL: {"group_by"},
        PlotTypes.TEMPORAL: {"group_by", "temporal_slice"},
    }

    def __init__(
        self, xarray=None, source=None, pipeline=None, server=None, local_rendering=None
    ):
        """Create an instance of the AnalyticsExplorer class."""
        super().__init__(xarray, source, pipeline, server, local_rendering)

        if self.source is None:
            self.source = vtkXArrayRectilinearSource(
                input=self.xarray
            )  # To initialize the pipeline

        self.ui = None
        self._setup_vtk(pipeline)
        self._build_ui()

    # -------------------------------------------------------------------------
    # VTK Setup
    # -------------------------------------------------------------------------

    def _setup_vtk(self, pipeline=None):
        self.renderer = vtkRenderer(background=(0.8, 0.8, 0.8))
        self.interactor = vtkRenderWindowInteractor()
        self.render_window = vtkRenderWindow(off_screen_rendering=1)

        anariPass = vtkRenderingAnari.vtkAnariPass()
        self.renderer.SetPass(anariPass)

        anariDevice = anariPass.GetAnariDevice()
        anariDevice.SetupAnariDeviceFromLibrary("environment", "default", False)

        anariRenderer = anariPass.GetAnariRenderer()
        anariRenderer.SetSubtype("raycast")
        anariRenderer.SetParameterf("ambientRadiance", 0.8)

        # VisRTX specific settings
        # anariRenderer.SetParameterf("lightFalloff", 0.5)
        anariRenderer.SetParameterb("denoise", True)
        anariRenderer.SetParameteri("pixelSamples", 10)
        # anariRenderer.SetParameteri("ambientSamples", 5)

        self.render_window.AddRenderer(self.renderer)
        self.interactor.SetRenderWindow(self.render_window)
        self.interactor.GetInteractorStyle().SetCurrentStyleToTrackballCamera()

        # Need explicit geometry extraction when used with WASM
        tail = self.extend_pipeline(head=self.source, pipeline=pipeline)

        self.geometry = vtkGeometryFilter(input_connection=tail.output_port)
        self.mapper = vtkPolyDataMapper(
            input_connection=self.geometry.output_port,
        )

        self.actor = vtkActor(mapper=self.mapper, visibility=0)

        self.interactor.Initialize()

        axes_actor = vtkAxesActor()
        self.widget = vtkOrientationMarkerWidget()
        self.widget.SetOrientationMarker(axes_actor)
        self.widget.SetInteractor(self.interactor)
        self.widget.SetViewport(0.85, 0, 1, 0.15)
        self.widget.EnabledOn()
        self.widget.InteractiveOff()

    # -------------------------------------------------------------------------
    # Trame API
    # -------------------------------------------------------------------------

    def start(self, **kwargs):
        """Initialize the UI and start the server for XArray Viewer."""
        self.ui.server.start(**kwargs)

    @property
    async def ready(self):
        """Start and wait for the XArray Viewer corroutine to be ready."""
        await self.ui.ready

    @property
    def state(self):
        """Returns the current the trame server state."""
        return self.server.state

    @property
    def ctrl(self):
        """Returns the Controller for the trame server."""
        return self.server.controller

    # -------------------------------------------------------------------------
    # Plot Control Properties
    # -------------------------------------------------------------------------

    @property
    def plot_type(self):
        """Get the current plot type."""
        current_value = self.state.active_plot
        # Find the PlotType enum that matches the current value
        for plot_enum, plot_str in plot_options.items():
            if plot_str == current_value:
                return plot_enum
        return PlotTypes.ZONAL  # Default

    @plot_type.setter
    def plot_type(self, value):
        """Set the plot type. Accepts PlotTypes enum or string."""
        if isinstance(value, PlotTypes):
            self.state.active_plot = plot_options.get(value)
        elif isinstance(value, str):
            # Validate the string is a valid plot option
            if value in plot_options.values():
                self.state.active_plot = value
            else:
                valid_options = list(plot_options.values())
                msg = f"Invalid plot type: {value}. Valid options: {valid_options}"
                raise ValueError(msg)
        else:
            type_name = type(value).__name__
            msg = f"plot_type must be PlotTypes enum or string, not {type_name}"
            raise TypeError(msg)
        # Update the plot after changing type
        if self.plotting:
            # First update the plot config
            self.plotting.expose_plot_specific_config()
            # If the plot type doesn't require manual update, generate the plot
            if not self.state.show_update_button:
                self.plotting.update_plot()
            else:
                # For plots that require update button, still generate the plot
                # to provide immediate feedback when changed programmatically
                figure = self.plotting.generate_plot()
                self.ctrl.figure_update(figure)
        # Update the view
        self.ctrl.view_update()

    @property
    def group_by(self):
        """Get the current temporal grouping option."""
        current_value = self.state.group_by
        # Find the GroupBy enum that matches the current value
        for group_enum, group_str in group_options.items():
            if group_str == current_value:
                return group_enum
        return GroupBy.YEAR  # Default

    @group_by.setter
    def group_by(self, value):
        """Set the temporal grouping. Accepts GroupBy enum or string."""
        if isinstance(value, GroupBy):
            self.state.group_by = group_options.get(value)
        elif isinstance(value, str):
            # Validate the string is a valid group option
            if value in group_options.values():
                self.state.group_by = value
            else:
                valid_options = list(group_options.values())
                msg = (
                    f"Invalid group by option: {value}. Valid options: {valid_options}"
                )
                raise ValueError(msg)
        else:
            type_name = type(value).__name__
            msg = f"group_by must be GroupBy enum or string, not {type_name}"
            raise TypeError(msg)
        # Check if this property is relevant for the current plot type
        self._check_property_relevance("group_by")
        # Trigger plot update for properties that affect the plot
        self._trigger_plot_update()
        # Update the view
        self.ctrl.view_update()

    @property
    def zonal_axis(self):
        """Get the current zonal axis (Longitude or Latitude)."""
        return self.state.zonal_axis

    @zonal_axis.setter
    def zonal_axis(self, value):
        """Set the zonal axis. Accepts 'Longitude', 'Latitude', 'X', or 'Y'."""
        if value in zonal_axes:
            self.state.zonal_axis = value
        elif value in zonal_axes.values():
            # Convert X/Y to Longitude/Latitude
            for axis_name, axis_value in zonal_axes.items():
                if axis_value == value:
                    self.state.zonal_axis = axis_name
                    break
        else:
            valid_keys = list(zonal_axes.keys())
            valid_values = list(zonal_axes.values())
            msg = f"Invalid zonal axis: {value}. Valid options: {valid_keys} or {valid_values}"
            raise ValueError(msg)
        # Check if this property is relevant for the current plot type
        self._check_property_relevance("zonal_axis")
        # Trigger plot update for properties that affect the plot
        self._trigger_plot_update()
        # Update the view
        self.ctrl.view_update()

    @property
    def temporal_slice(self):
        """Get the current temporal slice index."""
        return self.state.temporal_slice

    @temporal_slice.setter
    def temporal_slice(self, value):
        """Set the temporal slice index."""
        if not isinstance(value, int):
            type_name = type(value).__name__
            msg = f"temporal_slice must be an integer, not {type_name}"
            raise TypeError(msg)
        if value < 0:
            raise ValueError("temporal_slice must be non-negative")
        max_slices = self.state.time_groups
        if value > max_slices:
            msg = f"temporal_slice {value} exceeds maximum {max_slices}"
            raise ValueError(msg)
        self.state.temporal_slice = value
        # Check if this property is relevant for the current plot type
        self._check_property_relevance("temporal_slice")
        # Trigger plot update for properties that affect the plot
        self._trigger_plot_update()
        # Update the view
        self.ctrl.view_update()

    @property
    def analysis_variable(self):
        """Get the currently selected variable for analysis."""
        return self.state.color_by

    @analysis_variable.setter
    def analysis_variable(self, value):
        """Set the variable to use for analysis."""
        # Validate that the variable exists in the dataset
        if self.source and self.source.input:
            available_vars = list(self.source.input.data_vars)
            if value not in available_vars and value is not None:
                msg = (
                    f"Invalid variable: {value}. Available variables: {available_vars}"
                )
                raise ValueError(msg)
        self.state.color_by = value
        # analysis_variable is used by all plot types, no need to check relevance
        # Trigger plot update when variable changes
        self._trigger_plot_update()
        # Update the view
        self.ctrl.view_update()

    @property
    def figure_height(self):
        """Get the figure height percentage."""
        return self.state.figure_height

    @figure_height.setter
    def figure_height(self, value):
        """Set the figure height percentage (0-100)."""
        if not isinstance(value, (int, float)):
            type_name = type(value).__name__
            msg = f"figure_height must be a number, not {type_name}"
            raise TypeError(msg)
        if not 0 <= value <= 100:
            raise ValueError("figure_height must be between 0 and 100")
        self.state.figure_height = value
        # figure_height is a UI property, not plot-specific
        # Update the view
        self.ctrl.view_update()

    def get_current_plot(self):
        """
        Get the current plot as a Plotly figure object.

        Returns:
            plotly.graph_objects.Figure: The current plot figure, or None if no plot is available.
        """
        if not self.plotting:
            return None

        # Generate and return the current plot
        return self.plotting.generate_plot()

    def _check_property_relevance(self, property_name):
        """
        Check if a property is relevant for the current plot type and warn if not.

        Args:
            property_name: Name of the property being set
        """
        current_plot_type = self.plot_type
        relevant_properties = self.PLOT_PROPERTY_RELEVANCE.get(current_plot_type, set())

        if property_name not in relevant_properties:
            plot_name = plot_options.get(current_plot_type, str(current_plot_type))
            warnings.warn(
                f"Property '{property_name}' is not used by plot type '{plot_name}'. "
                f"Relevant properties for this plot: {', '.join(sorted(relevant_properties)) if relevant_properties else 'none'}",
                UserWarning,
                stacklevel=3,
            )

    def _trigger_plot_update(self):
        """
        Helper method to trigger plot updates based on the current plot type.
        For plots that auto-update, calls update_plot().
        For plots that require manual update, generates and displays the plot immediately.
        """
        if self.plotting:
            # Check if this plot type auto-updates or requires button click
            if not self.state.show_update_button:
                # Auto-updating plot type (like ZONAL)
                self.plotting.update_plot()
            else:
                # Plot types that normally require button click
                # We still generate the plot for immediate feedback
                figure = self.plotting.generate_plot()
                self.ctrl.figure_update(figure)

    # -------------------------------------------------------------------------
    # UI
    # -------------------------------------------------------------------------

    def _build_ui(self, **kwargs):
        self.state.trame__title = "Analytics Explorer"

        # Initialize default state values for properties
        self.state.setdefault("active_plot", plot_options.get(PlotTypes.ZONAL))
        self.state.setdefault("group_by", group_options.get(GroupBy.YEAR))
        self.state.setdefault("zonal_axis", next(iter(zonal_axes.keys())))
        self.state.setdefault("temporal_slice", 0)
        self.state.setdefault("time_groups", 0)
        self.state.setdefault("figure_height", 50)

        ## New way to build UI
        with StandardExplorerLayout(
            explorer=self, title="Analytics Explorer"
        ) as self.ui:
            with self.ui.content:
                Pan3dAnalyticsView(
                    render_window=self.render_window,
                    local_rendering=self.local_rendering,
                    widget=[self.widget],
                )
            with self.ui.control_panel:
                RenderingSettings(
                    ctx_name="rendering",
                    source=self.source,
                    update_rendering=self.update_rendering,
                )

            with v3.VNavigationDrawer(
                disable_resize_watcher=True,
                disable_route_watcher=True,
                permanent=True,
                location="right",
                v_model=("plot_drawer", False),
                width=800,
            ):
                self.plotting = Plotting(source=self.source, toggle="chart_expanded")

        self.ctx.save_dialog.save_callback = self._save_dataset
        if self.source and self.source.input is not None:
            self.ctx.rendering.update_from_source(self.source)

    # -----------------------------------------------------
    # State change callbacks
    # -----------------------------------------------------

    @change("color_by", "color_preset", "color_min", "color_max", "nan_color")
    def _on_color_properties_change(self, **kwargs):
        super()._on_color_properties_change(**kwargs)
        self.plotting.update_plot()

    @change("scale_x", "scale_y", "scale_z")
    def _on_scale_change(self, scale_x, scale_y, scale_z, **_):
        self.actor.SetScale(
            to_float(scale_x),
            to_float(scale_y),
            to_float(scale_z),
        )

        if self.state.import_pending:
            return

        if self.actor.visibility:
            self.renderer.ResetCamera()
            if self.local_rendering:
                self.ctrl.view_update(push_camera=True)
            self.ctrl.view_reset_camera()

    def update_rendering(self, reset_camera=False):
        self.state.dirty_data = False

        if self.actor.visibility == 0:
            self.actor.visibility = 1
            self.renderer.AddActor(self.actor)
            self.renderer.ResetCamera()
            if self.ctrl.view_update_force.exists():
                self.ctrl.view_update_force(push_camera=True)

        if reset_camera:
            self.ctrl.view_reset_camera()
        else:
            self.ctrl.view_update()


# -----------------------------------------------------------------------------
# Main executable
# -----------------------------------------------------------------------------


def main():
    app = AnalyticsExplorer()
    app.start()


if __name__ == "__main__":
    main()
