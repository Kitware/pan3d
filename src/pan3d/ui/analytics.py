import hashlib
import sys

from trame.decorators import TrameApp, change
from trame.widgets import html, plotly
from trame.widgets import vuetify3 as v3

try:
    import logging

    import xcdat  # noqa: F401

    logging.getLogger().setLevel(logging.CRITICAL + 1)
except ModuleNotFoundError as e:
    print(
        f"""
        Error occurred while importing xcdat required for Analytics Explorer: {e}
        Please make sure xcdat is installed properly using conda -- `conda install -c conda-forge xcdat`
        You may want to create a new conda environment an reinstall pan3d within along with xcdat.
        """
    )
    sys.exit(1)
from enum import Enum

import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from pan3d.xarray.algorithm import to_isel


class PlotTypes(Enum):
    ZONAL = (0,)
    ZONALTIME = (1,)
    GLOBAL = (2,)
    TEMPORAL = (3,)


plot_options = {
    PlotTypes.ZONAL: "Zonal Average",
    PlotTypes.ZONALTIME: "Zonal Average w/ Time",
    PlotTypes.GLOBAL: "Global Average",
    PlotTypes.TEMPORAL: "Temporal Average",
}


class GroupBy(Enum):
    HOUR = 0
    DAY = 1
    MONTH = 2
    SEASON = 3
    YEAR = 4
    NONE = 5


group_options = {
    GroupBy.HOUR: "Hour",
    GroupBy.DAY: "Day",
    GroupBy.MONTH: "Month",
    GroupBy.SEASON: "Season",
    GroupBy.YEAR: "Year",
    GroupBy.NONE: "None",
}

zonal_axes = {
    "Longitude": "X",
    "Latitude": "Y",
}


class CacheEntry:
    def __init__(self, data, figure):
        self.data = data
        self.figure = figure


@TrameApp()
class Plotting(v3.VCard):
    def __init__(
        self,
        source=None,
        **kwargs,
    ):
        super().__init__(
            rounded=True,
            classes="h-100",
            **kwargs,
        )
        self.source = source
        self.spatial_cache = {}
        self.temporal_cache = {}
        self.zonal_cache = {}

        # State variables controlling the UI for various types of plots
        self.state.figure_height = 50
        self.state.show_group_by = False
        self.state.show_temporal_slider = False
        self.state.show_zonal_axis = True
        self.state.show_update_button = False

        with self:
            with v3.VCardTitle():
                with html.Div(classes="d-flex"):
                    v3.VSelect(
                        label="Plot Type",
                        v_model=("active_plot", plot_options.get(PlotTypes.ZONAL)),
                        items=("plots", list(plot_options.values())),
                        hide_details=True,
                        variant="outlined",
                        density="compact",
                    )
                v3.VDivider(classes="my-2")
                with html.Div(classes="d-flex"):
                    v3.VSelect(
                        v_show="show_zonal_axis",
                        label="Zonal Axis",
                        v_model=("zonal_axis", next(iter(zonal_axes.keys()))),
                        items=("axes", list(zonal_axes.keys())),
                        hide_details=True,
                        variant="outlined",
                        density="compact",
                    )
                    v3.VSelect(
                        v_show="show_group_by",
                        label="Group By",
                        v_model=("group_by", group_options.get(GroupBy.YEAR)),
                        items=("groups", list(group_options.values())),
                        hide_details=True,
                        variant="outlined",
                        density="compact",
                    )
                with html.Div(
                    v_if="show_temporal_slider",
                ):
                    html.Div("Temporal Slice Selection")
                    v3.VSlider(
                        v_model=("temporal_slice", 0),
                        min=0,
                        max=("time_groups", 0),
                        step=1,
                        hide_details=True,
                        density="compact",
                    )
                v3.VDivider(classes="my-2")
                with html.Div(
                    v_if="show_update_button", classes="text-center align-center"
                ):
                    v3.VBtn("Update Plots", click=self.update_plot)
            with v3.VCardText(style=("`height: ${figure_height}%;`",)):
                figure = plotly.Figure(
                    display_logo=True,
                    display_mode_bar=True,
                )
                self.ctrl.figure_update = figure.update

    def expose_plot_specific_config(self):
        """
        Toggle visibility of components controlling plots based on chosen type
        """
        state = self.state
        plot_type = state.active_plot

        # Default values
        config = {
            "figure_height": 50,
            "show_zonal_axis": False,
            "show_group_by": True,
            "show_temporal_slider": False,
            "show_update_button": True,
        }

        # Overrides for each plot type
        plot_overrides = {
            plot_options.get(PlotTypes.ZONAL): {
                "show_zonal_axis": True,
                "show_group_by": False,
                "show_update_button": False,
            },
            plot_options.get(PlotTypes.ZONALTIME): {
                "figure_height": 80,
                "show_zonal_axis": True,
            },
            plot_options.get(PlotTypes.GLOBAL): {
                "show_zonal_axis": False,
            },
            plot_options.get(PlotTypes.TEMPORAL): {
                "show_temporal_slider": True,
            },
        }

        # Merge overrides only if the plot type exists in the dictionary
        config.update(plot_overrides.get(plot_type, {}))

        # Update state in a single call
        state.update(config)

    def get_key(self, selection):
        return hashlib.sha256(repr(selection).encode()).hexdigest()

    def get_selection_criteria(self, full_temporal=False):
        """
        Get the xarray slicing criteria based on current selection of data
        """
        slices = self.source.slices
        (x, y, z, t) = (self.source.x, self.source.y, self.source.z, self.source.t)
        if full_temporal:
            return to_isel(slices, x, y, z)
        return to_isel(slices, x, y, z, t)

    def apply_spatial_average(self, axis=None):
        """
        Calculate spatial average of data for the current selected time
        """
        if axis is None:
            axis = ["X"]
        ds = self.source.input
        active_var = self.state.color_by
        select = self.get_selection_criteria()
        return ds.isel(select).spatial.average(active_var, axis=axis)

    def apply_spatial_average_full_temporal(self, axis=None):
        """
        Calculate spatial average for data for full temporal resoulution
        """
        ds = self.source.input
        active_var = self.state.color_by
        select = self.get_selection_criteria(full_temporal=True)
        # Apply spatial average
        if axis is not None:
            average = ds.isel(select).spatial.average(active_var, axis)
        else:
            average = ds.isel(select).spatial.average(active_var)
        # Optionally apply temporal grouping
        group_by = self.state.group_by

        if group_by == group_options.get(GroupBy.NONE):
            return average

        return average.temporal.group_average(
            active_var, freq=group_by.lower(), weighted=True
        )

    def apply_temporal_average(self, active_var):
        """
        Calculate time based average for data
        """
        ds = self.source.input
        select = self.get_selection_criteria(full_temporal=True)
        group_by = self.state.group_by
        if group_by == group_options.get(GroupBy.NONE):
            return ds.isel(select).temporal.average(active_var, weighted=True)
        return ds.isel(select).temporal.group_average(
            active_var, freq=group_by.lower(), weighted=True
        )

    def generate_plot(self):
        state = self.state
        active_var = self.state.color_by
        (x, y, _, t) = (self.source.x, self.source.y, self.source.z, self.source.t)
        if active_var is None:
            return None

        plot_type = state.active_plot
        zonal_axis = state.zonal_axis
        axis = x if zonal_axes.get(zonal_axis) == "X" else y
        if plot_type == plot_options.get(PlotTypes.ZONAL):
            return self.zonal_average(active_var, axis)
        if plot_type == plot_options.get(PlotTypes.ZONALTIME):
            return self.zonal_with_time(active_var, axis, t)
        if plot_type == plot_options.get(PlotTypes.GLOBAL):
            return self.global_full_temporal(active_var, t)
        if plot_type == plot_options.get(PlotTypes.TEMPORAL):
            return self.temporal_average(active_var, x, y, t)
        return None

    def zonal_average(self, active_var, axis):
        """
        Get a plotly figure for the zonal average for current sptio-temporal selection.
        Average is calculated over a certain specified spatial dimension (Longitude or Latitude).
        """
        data = self.apply_spatial_average(axis=zonal_axes.get(self.state.zonal_axis))
        to_plot = data[active_var]
        dim = to_plot.dims[0]
        plot = px.line(x=to_plot[dim].to_numpy(), y=to_plot.to_numpy())

        var_long_name = data[active_var].attrs.get("long_name", active_var)
        var_units = data[active_var].attrs.get("units", "")
        x_axis_name = data[dim].attrs.get("long_name", dim)
        plot.update_layout(
            title=f'Zonal Average for {active_var} "{var_long_name}" over {axis} (unit: {var_units})',
            xaxis_title=x_axis_name,
            yaxis_title=var_long_name,
        )
        return plot

    def zonal_with_time(self, active_var, axis, t):
        """
        Get a plotly figure for the zonal average along with current and full temporal selection.
        Average is calculated over a certain specified spatial dimension (Longitude or Latitude).
        """
        data_t = self.apply_spatial_average(axis=zonal_axes.get(self.state.zonal_axis))
        data = self.apply_spatial_average_full_temporal(
            axis=zonal_axes.get(self.state.zonal_axis)
        )

        var_long_name = data[active_var].attrs.get("long_name", active_var)
        var_units = data[active_var].attrs.get("units", "")
        figure = make_subplots(
            rows=2,
            cols=1,
            subplot_titles=(
                f'Zonal Average for {active_var} "{var_long_name}" at {t} = {self.state.slice_t} (unit: {var_units})',
                f"Zonal Average for {var_long_name}",
            ),
        )
        to_plot = data_t[active_var]
        dim = to_plot.dims[0]
        x_axis_name = data[dim].attrs.get("long_name", dim)
        plot = px.line(x=to_plot[dim], y=to_plot)
        for trace in plot.data:
            figure.add_trace(trace, row=1, col=1)
        figure.update_xaxes(title_text=x_axis_name, row=1, col=1)
        figure.update_yaxes(title_text=var_long_name, row=1, col=1)

        taxis = self.get_time_labels(data[t])
        plot = px.imshow(data[active_var], y=taxis)
        plot.update_layout(coloraxis_colorbar={"orientation": "h"})
        for trace in plot.data:
            figure.add_trace(trace, row=2, col=1)
        figure.update_xaxes(title_text=x_axis_name, row=2, col=1)
        figure.update_yaxes(title_text=t, row=2, col=1)

        return figure

    def global_full_temporal(self, active_var, t):
        """
        Get a plotly figure for the global average for all data with full temporal resolution.
        Data from spatial dimension is averaged yielding a single quantity with tempoal dimension.
        """
        data = self.apply_spatial_average_full_temporal(axis=None)
        time = self.get_time_labels(data[t])
        plot = px.line(x=time, y=data[active_var])
        # plot.update_layout(title_text=f"Global Average for {active_var}")

        var_long_name = data[active_var].attrs.get("long_name", active_var)
        var_units = data[active_var].attrs.get("units", "")
        x_axis_name = data[t].attrs.get("long_name", t)
        plot.update_layout(
            title=f'Global average for {active_var} "{var_long_name}" (unit: {var_units})',
            xaxis_title=x_axis_name,
            yaxis_title=var_long_name,
        )
        return plot

    def temporal_average(self, active_var, x, y, t):
        """
        Get a time based average of data, data in temporal domain in averaged keeping spatial dimensions same
        """
        data = self.apply_temporal_average(active_var)
        self.state.time_groups = len(data[t])
        slice = self.state.temporal_slice
        plot = px.imshow(data[active_var][slice])
        plot.update_yaxes(autorange="reversed")
        var_long_name = data[active_var].attrs.get("long_name", active_var)
        var_units = data[active_var].attrs.get("units", "")
        x_axis_name = data[x].attrs.get("long_name", x)
        y_axis_name = data[y].attrs.get("long_name", y)
        plot.update_layout(
            title=f'Temporal average for {active_var} "{var_long_name}" (unit: {var_units}) at time {slice}/{len(data[t])}',
            xaxis_title=x_axis_name,
            yaxis_title=y_axis_name,
            coloraxis_colorbar={"orientation": "h"},
        )

        return plot

    def get_time_labels(self, time_array):
        group_by = self.state.group_by
        if group_by == group_options.get(GroupBy.YEAR):
            return np.vectorize(lambda dt: f"{dt.year}")(time_array)
        if group_by == group_options.get(GroupBy.MONTH):
            return np.vectorize(lambda dt: f"{dt.month}-{dt.year}")(time_array)
        return np.vectorize(lambda dt: f"{dt.isoformat()}")(time_array)

    @change("temporal_slice")
    def on_change_group(self, **kwargs):
        active_var = self.state.color_by
        (x, y, _, t) = (self.source.x, self.source.y, self.source.z, self.source.t)
        if active_var is None:
            return
        plot = self.temporal_average(active_var, x, y, t)
        self.ctrl.figure_update(plot)

    @change(
        "zonal_axis",
        "slice_t",
        "slice_x_range",
        "slice_y_range",
        "slice_z_range",
    )
    def update_plot(self, **kwargs):
        figure = self.generate_plot()
        self.ctrl.figure_update(figure)

    @change("active_plot")
    def on_change_active_plot(self, **kwargs):
        self.expose_plot_specific_config()
        plot_type = self.state.active_plot
        if plot_type != plot_options.get(PlotTypes.ZONAL):
            self.ctrl.figure_update(go.Figure())
            return
        figure = self.generate_plot()
        self.ctrl.figure_update(figure)
