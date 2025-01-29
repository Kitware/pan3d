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
                    v3.VSelect(
                        label="Group By",
                        v_model=("group_by", group_options.get(GroupBy.YEAR)),
                        items=("groups", list(group_options.values())),
                        hide_details=True,
                        variant="outlined",
                        density="compact",
                    )
                    # v_show = (
                    #    f"active_plot === {plot_options.get(PlotTypes.TEMPORAL)}",
                    # )
                with html.Div(classes="d-flex"):
                    v3.VSlider(
                        v_model=("active_group", 0),
                        min=0,
                        max=("time_groups", 0),
                        step=1,
                        hide_details=True,
                        density="compact",
                    )

            with v3.VCardText(style="position: absolute; height: 80%"):
                figure = plotly.Figure(
                    figure=go.Figure(),
                    display_logo=True,
                    display_mode_bar=True,
                )
                self.ctrl.figure_update = figure.update

        self.on_change_active_plot()

    def get_key(self):
        for_key = [
            self.state.slice_x_range,
            self.state.slice_y_range,
            self.state.slice_z_range,
        ]
        return hashlib.sha256(repr(for_key).encode()).hexdigest()

    def get_selection_criteria(self):
        slices = self.source.slices
        (x, y, z, t) = (self.source.x, self.source.y, self.source.z, self.source.t)
        select = to_isel(slices, x, y, z, t)
        return select

    def get_selection_criteria_full_temporal(self):
        slices = self.source.slices
        (x, y, z) = (self.source.x, self.source.y, self.source.z)
        select = to_isel(slices, x, y, z)
        return select

    def apply_spatial_average(self, axis=["X"]):
        ds = self.source.input
        active_var = self.state.color_by
        select = self.get_selection_criteria()
        if select is None:
            return None
        return ds.isel(select).spatial.average(active_var, axis)

    def apply_spatial_average_full_temporal(self, axis=["X"]):
        ds = self.source.input
        active_var = self.state.color_by
        select = self.get_selection_criteria_full_temporal()

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
        ds = self.source.input
        select = self.get_selection_criteria_full_temporal()
        group_by = self.state.group_by.lower()
        selection = ds.isel(select)
        print(selection)
        avg = ds.temporal.group_average(active_var, freq=group_by, weighted=True)
        return avg

    def generate_plot(self):
        active_var = self.state.color_by
        (x, y, _, t) = (self.source.x, self.source.y, self.source.z, self.source.t)

        print(self.state.active_plot, active_var)
        # figure = go.Figure()
        if active_var is None:
            return None

        key = self.get_key()

        if self.state.active_plot == plot_options.get(PlotTypes.ZONAL):
            return self.zonal_average(active_var, x)
        elif self.state.active_plot == plot_options.get(PlotTypes.ZONALTIME):
            return self.zonal_with_time(active_var, x, t, key)
        elif self.state.active_plot == plot_options.get(PlotTypes.GLOBAL):
            return self.global_full_temporal(active_var, t, key)
        elif self.state.active_plot == plot_options.get(PlotTypes.TEMPORAL):
            return self.temporal_average(active_var, x, y)

    def temporal_average(self, x, y, active_var):
        figure = go.Figure()
        data = self.apply_temporal_average(active_var)
        plot = go.Heatmap(
            z=data[active_var][0], x=data[x], y=data[y], colorscale="Viridis"
        )
        figure.add_trace(plot)
        figure.update_layout(title_text=f"Temporal Average for {active_var}")
        return figure

    def zonal_average(self, active_var, axis):
        figure = go.Figure()
        data = self.apply_spatial_average()
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

    def zonal_with_time(self, active_var, axis, t, key):
        print("Here Here!!!!")
        figure = make_subplots(
            rows=2,
            cols=1,
            subplot_titles=(
                f"Zonal Average at {t} = {self.state.slice_t}",
                f"Zonal Average for {active_var} with full temporal resolution",
            ),
        )

        data = self.apply_spatial_average()
        figure.add_trace(
            go.Line(x=data[axis], y=data[active_var], mode="lines", name="Spatial Avg"),
            row=1,
            col=1,
        )

        data = self.apply_spatial_average_full_temporal(axis=["X"])
        time = self.get_time_labels(data[t])
        plot = go.Heatmap(
            z=data[active_var], x=data[axis], y=time, colorscale="Viridis"
        )
        figure.add_trace(plot, row=2, col=1)
        figure.update_layout(title_text=f"Zonal Average for {active_var} over {axis}")
        return figure

    def global_full_temporal(self, active_var, t, key):
        figure = go.Figure()
        data = self.apply_spatial_average_full_temporal(axis=None)
        time = self.get_time_labels(data[t])
        plot = go.Scatter(x=time, y=data[active_var], mode="lines", name="Spatial Avg")
        self.spatial_cache[key] = plot
        figure.add_trace(plot)
        figure.update_layout(title_text=f"Global Average for {active_var}")
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
        print("Updating figure")

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
        print(
            f"Parameters : var {active_var}, x {x}, y {y}, time_group {time_group}", avg
        )
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
        "group_by",
        "slice_t",
        "slice_x_range",
        "slice_y_range",
        "slice_z_range",
    )
    def on_change_active_plot(self, **kwargs):
        figure = self.generate_plot()
        print("plot generated successfully")
        print(figure)
        self.ctrl.figure_update(figure)
