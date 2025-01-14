from trame.decorators import TrameApp, change
from trame.widgets import vuetify3 as v3, plotly

import xcdat  # noqa
import plotly.graph_objects as go
from plotly.subplots import make_subplots

PLOTS = [
    "Zonal Average",
    "Zonal Average w/ Time",
    "Spatial Average",
    "Temporal Average",
]


@TrameApp()
class Plotting(v3.VCard):
    def __init__(
        self,
        source=None,
        toggle=None,
        **kwargs,
    ):
        super().__init__(
            rounded=(f"{toggle} || 'circle'",),
            classes=(f"`controllerbr ${{ {toggle} ? 'w-50 h-50' : ''}}`",),
            **kwargs,
        )
        self.source = source
        self.spatial_cache = {}
        self.temporal_cache = {}
        self.zonal_cache = {}

        with self:
            with v3.VCardText(
                v_show=(toggle, True),
                classes="pa-0",
                style="height: calc(100% - 3.7rem)",
            ):
                figure = plotly.Figure(
                    figure=go.Figure(),
                    display_logo=True,
                    display_mode_bar=True,
                )
                self.ctrl.figure_update = figure.update

            with v3.VCardTitle(
                classes=(
                    f"`d-flex bg-white ${{ {toggle} ? 'rounded-b border-t-thin':'rounded-circle'}}`",
                ),
            ):
                v3.VSelect(
                    v_if=toggle,
                    label="Plot Type",
                    v_model=("active_plot", PLOTS[0]),
                    items=("plots", PLOTS),
                    hide_details=True,
                    dense=True,
                    variant="outlined",
                    density="compact",
                )
                v3.VBtn(
                    icon="mdi-close",
                    v_if=toggle,
                    click=f"{toggle} = !{toggle}",
                    flat=True,
                    size="sm",
                )
                v3.VBtn(
                    icon="mdi-chart-line",
                    v_else=True,
                    click=f"{toggle} = !{toggle}",
                    flat=True,
                    size="sm",
                )

    def generate_plot(self):
        ds = self.source.input
        slices = self.source.slices
        x = self.source.x
        y = self.source.y
        z = self.source.z
        t = self.source.t
        from pan3d.xarray.algorithm import to_isel

        select = to_isel(slices, x, y, z, t)
        if select is None:
            return None
        all_t = select.copy()
        all_t.pop(t)
        print(all_t)
        active_var = self.state.color_by
        figure = go.Figure()
        if active_var is None:
            return figure

        import hashlib

        for_key = [
            self.state.slice_x_range,
            self.state.slice_y_range,
            self.state.slice_z_range,
        ]
        key = hashlib.sha256(repr(for_key).encode()).hexdigest()

        if self.state.active_plot == PLOTS[0]:
            selection = ds.isel(select)
            avg = selection.spatial.average(active_var, axis=["X"])
            # figure.add_trace(go.Scatter(x=avg.time, y=avg[active_var], mode="lines", name="Spatial Avg"))
            figure.add_trace(
                go.Line(x=avg[x], y=avg[active_var], mode="lines", name="Spatial Avg")
            )

            # Customize the layout
            figure.update_layout(
                title=f"Zonal Average for {active_var} over {x}",
                xaxis_title=x,
                yaxis_title=active_var,
                template="plotly_white",
            )
            return figure

        elif self.state.active_plot == PLOTS[1]:
            figure = make_subplots(
                rows=1,
                cols=2,
                subplot_titles=(
                    f"Zonal Average at {t} = {self.state.slice_t}",
                    f"Zonal Average over {t}",
                ),
                column_widths=[0.5, 0.5],
            )

            selection = ds.isel(select)
            avg = selection.spatial.average(active_var, axis=["X"])
            figure.add_trace(
                go.Line(x=avg[x], y=avg[active_var], mode="lines", name="Spatial Avg"),
                row=1,
                col=1,
            )

            selection = ds.isel(all_t)
            if self.zonal_cache.get(key) is not None:
                plot = self.zonal_cache[key]
                figure.add_trace(plot, row=1, col=2)
            else:
                # Plot concurrently
                avg = selection.spatial.average(active_var, axis=["X"])
                plot = go.Heatmap(
                    z=avg[active_var], x=avg[x], y=avg[y], colorscale="Viridis"
                )
                self.zonal_cache[key] = plot
                figure.add_trace(plot, row=1, col=2)
            figure.update_layout(title_text=f"Zonal Average for {active_var} over {x}")
            return figure

        elif self.state.active_plot == PLOTS[2]:
            selection = ds
            if self.spatial_cache.get(key) is not None:
                plot = self.spatial_cache[key]
                figure.add_trace(plot)
            else:
                # Plot concurrently
                avg = selection.spatial.average(active_var)
                plot = go.Scatter(
                    x=avg[t], y=avg[active_var], mode="lines", name="Spatial Avg"
                )
                self.spatial_cache[key] = plot
                figure.add_trace(plot)
            figure.update_layout(
                title_text=f"Spatial Average for {active_var} over {x}"
            )
            return figure

        elif self.state.active_plot == PLOTS[3]:
            selection = ds
            if self.temporal_cache.get(key) is not None:
                plot = self.temporal_cache[key]
                figure.add_trace(plot)
            else:
                # Plot concurrently
                avg = selection.spatial.average(active_var)
                plot = go.Scatter(
                    x=avg[t], y=avg[active_var], mode="lines", name="Spatial Avg"
                )
                self.temporal_cache[key] = plot
                figure.add_trace(plot)
            figure.update_layout(
                title_text=f"Spatial Average for {active_var} over {x}"
            )
            return figure

    @change("active_plot", "slice_t", "slice_x_range", "slice_y_range", "slice_z_range")
    def on_change_active_plot(self, **kwargs):
        figure = self.generate_plot()
        self.ctrl.figure_update(figure)
