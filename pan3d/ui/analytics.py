from trame.decorators import TrameApp, change
from trame.widgets import vuetify3 as v3, plotly, html

import hashlib
import xcdat  # noqa
import numpy as np
from enum import Enum

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
                        v_model=("zonal_axis", list(zonal_axes.keys())[0]),
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
                v3.VDivider(classes="my-2")
                with html.Div(
                    v_if="show_temporal_slider",
                ):
                    html.Span("Temporal Slice Selection")
                    v3.VSlider(
                        v_model=("active_group", 0),
                        min=0,
                        max=("time_groups", 0),
                        step=1,
                        hide_details=True,
                        density="compact",
                    )

            with v3.VCardText(style=("`height: ${figure_height}%;`",)):
                figure = plotly.Figure(
                    figure=go.Figure(),
                    display_logo=True,
                    display_mode_bar=True,
                )
                self.ctrl.figure_update = figure.update

        self.on_change_active_plot()

    def expose_plot_specific_config(self):
        """
        Toggle visibility of components controlling plots based on chosen type
        """
        state = self.state
        plot_type = state.active_plot
        if plot_type == plot_options.get(PlotTypes.ZONAL):
            state.figure_height = 50
            state.show_zonal_axis = True
            state.show_group_by = False
            state.show_temporal_slider = False
        if plot_type == plot_options.get(PlotTypes.ZONALTIME):
            state.figure_height = 80
            state.show_zonal_axis = True
            state.show_group_by = True
            state.show_temporal_slider = False
        if plot_type == plot_options.get(PlotTypes.GLOBAL):
            state.figure_height = 50
            state.show_zonal_axis = False
            state.show_group_by = True
            state.show_temporal_slider = False
        if plot_type == plot_options.get(PlotTypes.TEMPORAL):
            state.figure_height = 50
            state.show_zonal_axis = False
            state.show_group_by = True
            state.show_temporal_slider = True

    def get_key(self):
        for_key = [
            self.state.slice_x_range,
            self.state.slice_y_range,
            self.state.slice_z_range,
        ]
        return hashlib.sha256(repr(for_key).encode()).hexdigest()

    def get_selection_criteria(self, full_temporal=False):
        """
        Get the xarray slicing criteria based on current selection of data
        """
        slices = self.source.slices
        (x, y, z, t) = (self.source.x, self.source.y, self.source.z, self.source.t)
        if full_temporal:
            return to_isel(slices, x, y, z)
        else:
            return to_isel(slices, x, y, z, t)

    def apply_spatial_average(self, axis=["X"]):
        """
        Calculate spatial average of data for the current selected time
        """
        ds = self.source.input
        active_var = self.state.color_by
        select = self.get_selection_criteria()
        return ds.isel(select).spatial.average(active_var, axis=axis)

    def apply_spatial_average_full_temporal(self, axis=["X"]):
        """
        Calculate spatial average for data for full temporal resoulution
        """
        ds = self.source.input
        active_var = self.state.color_by
        select = self.get_selection_criteria(full_temporal=True)

        group_by = self.state.group_by
        average = (
            ds.isel(select).spatial.average(active_var, axis)
            if axis is not None
            else ds.isel(select).spatial.average(active_var)
        )
        if group_by == group_options.get(GroupBy.NONE):
            return average
        else:
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
        else:
            return ds.isel(select).temporal.group_average(
                active_var, freq=group_by.lower(), weighted=True
            )

    def generate_plot(self):
        state = self.state
        state.figure_height = 50
        active_var = self.state.color_by
        (x, y, _, t) = (self.source.x, self.source.y, self.source.z, self.source.t)
        if active_var is None:
            return None

        self.expose_plot_specific_config()

        plot_type = state.active_plot
        zonal_axis = state.zonal_axis
        axis = x if zonal_axes.get(zonal_axis) == "X" else y
        if plot_type == plot_options.get(PlotTypes.ZONAL):
            return self.zonal_average(active_var, axis)
        elif plot_type == plot_options.get(PlotTypes.ZONALTIME):
            return self.zonal_with_time(active_var, axis, t)
        elif plot_type == plot_options.get(PlotTypes.GLOBAL):
            return self.global_full_temporal(active_var, t)
        elif plot_type == plot_options.get(PlotTypes.TEMPORAL):
            return self.temporal_average(active_var, x, y, t)

    def zonal_average(self, active_var, axis):
        """
        Get a plotly figure for the zonal average for current sptio-temporal selection.
        Average is calculated over a certain specified spatial dimension (Longitude or Latitude).
        """
        figure = go.Figure()
        data = self.apply_spatial_average(axis=zonal_axes.get(self.state.zonal_axis))
        figure.add_trace(
            go.Line(x=data[axis], y=data[active_var], mode="lines", name="Spatial Avg")
        )
        figure.update_layout(
            title=f"Zonal Average for {active_var} over {axis}",
            xaxis_title=axis,
            yaxis_title=active_var,
            template="plotly_white",
        )
        return figure

    def zonal_with_time(self, active_var, axis, t):
        """
        Get a plotly figure for the zonal average along with current and full temporal selection.
        Average is calculated over a certain specified spatial dimension (Longitude or Latitude).
        """
        figure = make_subplots(
            rows=2,
            cols=1,
            subplot_titles=(
                f"Zonal Average at {t} = {self.state.slice_t}",
                f"Zonal Average for {active_var} with full temporal resolution",
            ),
        )

        data = self.apply_spatial_average(axis=zonal_axes.get(self.state.zonal_axis))
        figure.add_trace(
            go.Line(x=data[axis], y=data[active_var], mode="lines", name="Spatial Avg"),
            row=1,
            col=1,
        )
        import time

        data = self.apply_spatial_average_full_temporal(
            axis=zonal_axes.get(self.state.zonal_axis)
        )
        taxis = self.get_time_labels(data[t])
        s = time.time()
        plot = go.Heatmap(
            # data[active_var], labels=dict(x=axis, y="Time"), color_continuous_scale="Viridis"
            z=data[active_var],
            x=data[axis],
            y=taxis,
            colorscale="Viridis",
        )
        e = time.time()
        print("Time to produce plot : ", e - s)
        figure.add_trace(plot, row=2, col=1)
        figure.update_layout(title_text=f"Zonal Average for {active_var} over {axis}")
        return figure

    def global_full_temporal(self, active_var, t):
        """
        Get a plotly figure for the global average for all data with full temporal resolution.
        Data from spatial dimension is averaged yielding a single quantity with tempoal dimension.
        """
        figure = go.Figure()
        data = self.apply_spatial_average_full_temporal(axis=None)
        time = self.get_time_labels(data[t])
        plot = go.Scatter(x=time, y=data[active_var], mode="lines", name="Spatial Avg")
        figure.add_trace(plot)
        figure.update_layout(title_text=f"Global Average for {active_var}")
        return figure

    def temporal_average(self, active_var, x, y, t):
        """
        Get a time based average of data, data in temporal domain in averaged keeping spatial dimensions same
        """
        figure = go.Figure()
        data = self.apply_temporal_average(active_var)
        plot = go.Heatmap(
            z=data[active_var][0], x=data[x], y=data[y], colorscale="Viridis"
        )
        figure.add_trace(plot)
        figure.update_layout(title_text=f"Temporal Average for {active_var}")
        return figure

    def get_time_labels(self, time_array):
        group_by = self.state.group_by
        if group_by == group_options.get(GroupBy.YEAR):
            return np.vectorize(lambda dt: f"{dt.year}")(time_array)
        if group_by == group_options.get(GroupBy.MONTH):
            return np.vectorize(lambda dt: f"{dt.month}-{dt.year}")(time_array)
        else:
            return np.vectorize(lambda dt: f"{dt.isoformat()}")(time_array)

    @change("active_group")
    def on_change_group(self, **kwargs):
        import hashlib

        for_key = [
            self.state.slice_x_range,
            self.state.slice_y_range,
            self.state.slice_z_range,
        ]
        key = hashlib.sha256(repr(for_key).encode()).hexdigest()

        x = self.source.x
        y = self.source.y

        active_var = self.state.color_by
        time_group = int(self.state.active_group)
        entry = self.temporal_cache.get(key)

        if entry is None:
            return

        avg = entry.data
        plot = go.Heatmap(
            z=avg[active_var][time_group], x=avg[x], y=avg[y], colorscale="Viridis"
        )
        self.temporal_cache[key] = CacheEntry(avg, plot)

        figure = go.Figure()
        figure.add_trace(plot)
        figure.update_layout(title_text=f"Temporal Average for {active_var} over {x}")

        entry.figure = figure
        self.temporal_cache[key] = entry
        self.ctrl.figure_update(figure)

    @change(
        "active_plot",
        "zonal_axis",
        "group_by",
        "slice_t",
        "slice_x_range",
        "slice_y_range",
        "slice_z_range",
    )
    def on_change_active_plot(self, **kwargs):
        print("Updating plot")
        figure = self.generate_plot()
        self.ctrl.figure_update(figure)
