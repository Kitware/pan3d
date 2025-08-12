"""Summary toolbar widget for displaying time navigation and color selection."""

from trame.widgets import html
from trame.widgets import vuetify3 as v3


class SummaryToolbar(v3.VCard):
    """
    A toolbar widget that displays time navigation controls and color selection.

    This widget provides a compact interface for:
    - Displaying current time label
    - Time slider navigation
    - Time index display
    - Color by variable selection
    """

    def __init__(
        self,
        t_labels="t_labels",
        slice_t="slice_t",
        slice_t_max="slice_t_max",
        color_by="color_by",
        data_arrays="data_arrays",
        max_time_width="max_time_width",
        max_time_index_width="max_time_index_width",
        **kwargs,
    ):
        """
        Initialize the SummaryToolbar widget.

        Parameters:
            t_labels: State variable name for time labels list
            slice_t: State variable name for current time index
            slice_t_max: State variable name for maximum time index
            color_by: State variable name for color by selection
            data_arrays: State variable name for available data arrays
            max_time_width: State variable name for max time label width
            max_time_index_width: State variable name for max time index width
            **kwargs: Additional arguments passed to VCard
        """
        super().__init__(
            classes="summary-toolbar",
            rounded="pill",
            **kwargs,
        )

        # Activate CSS - these modules should be imported and enabled at app level
        from pan3d.ui.css import base, preview

        self.server.enable_module(base)
        self.server.enable_module(preview)

        with self:
            with v3.VToolbar(
                classes="pl-2",
                height=50,
                elevation=1,
                style="background: none;",
            ):
                v3.VIcon("mdi-clock-outline")
                html.Pre(
                    f"{{{{ {t_labels}[slice_t] }}}}",
                    classes="mx-2 text-left",
                    style=(f"`min-width: ${{ {max_time_width} }}rem;`",),
                )
                v3.VSlider(
                    prepend_inner_icon="mdi-clock-outline",
                    v_model=(slice_t, 0),
                    min=0,
                    max=(slice_t_max, 0),
                    step=1,
                    hide_details=True,
                    density="compact",
                    flat=True,
                    variant="solo",
                    classes="mx-2",
                )
                html.Div(
                    f"{{{{ {slice_t} + 1 }}}}/{{{{ {slice_t_max} + 1 }}}}",
                    classes="mx-2 text-right",
                    style=(f"`min-width: ${{ {max_time_index_width} }}rem;`",),
                )
                v3.VSelect(
                    placeholder="Color By",
                    prepend_inner_icon="mdi-format-color-fill",
                    v_model=(color_by, None),
                    items=(data_arrays, []),
                    clearable=True,
                    hide_details=True,
                    density="compact",
                    flat=True,
                    variant="solo",
                    max_width=200,
                )
