"""Clip Slice Control widget for axis clipping/cropping operations."""

from trame.widgets import html
from trame.widgets import vuetify3 as v3


class ClipSliceControl(html.Div):
    """
    A widget for controlling clipping/cropping along a specific axis.

    Provides range selection or single cut value for data clipping.
    """

    _next_id = 0

    def __init__(
        self,
        axis,
        axis_name_expr,
        bounds_min_expr,
        bounds_max_expr,
        extents_min_expr,
        extents_max_expr,
        # State variable names (optional)
        state_prefix=None,
        type_var=None,
        range_var=None,
        cut_var=None,
        step_expr=None,
        **kwargs,
    ):
        """
        Initialize the ClipSliceControl widget.

        Args:
            axis: The axis identifier (x, y, z)
            axis_name_expr: Expression for axis name (e.g., "axis_names[0]")
            bounds_min_expr: Expression for bounds min (e.g., "dataset_bounds[0]")
            bounds_max_expr: Expression for bounds max (e.g., "dataset_bounds[1]")
            extents_min_expr: Expression for extents min
            extents_max_expr: Expression for extents max
            state_prefix: Prefix for state variable names. If not provided, generates unique prefix.
            type_var: State variable for slice type (range/cut)
            range_var: State variable for range values
            cut_var: State variable for cut value
            step_expr: Expression for step value (for tooltip)
            **kwargs: Additional div properties
        """
        super().__init__(**kwargs)

        # Generate unique namespace if not provided
        ClipSliceControl._next_id += 1
        self._id = ClipSliceControl._next_id
        ns = state_prefix or f"clip_slice_{self._id}_{axis}"

        # Initialize state variable names
        self._state_vars = {
            "type": type_var or f"{ns}_type",
            "range": range_var or f"{ns}_range",
            "cut": cut_var or f"{ns}_cut",
            "step": step_expr or f"{ns}_step",
        }

        # Use provided variables or defaults for compatibility
        type_var = type_var or f"slice_{axis}_type"
        range_var = range_var or f"slice_{axis}_range"
        cut_var = cut_var or f"slice_{axis}_cut"
        step_expr = step_expr or f"slice_{axis}_step"

        with self:
            with v3.VTooltip(
                v_if=axis_name_expr,
                text=(
                    f"`${{{axis_name_expr}}}: [${{{bounds_min_expr}}}, ${{{bounds_max_expr}}}] "
                    f"${{{type_var} ==='range' ? ('(' + {range_var}.map((v,i) => v+1).concat({step_expr}).join(', ') + ')'): {cut_var}}}`"
                ),
            ):
                with html.Template(v_slot_activator="{ props }"):
                    with html.Div(
                        classes="d-flex",
                        v_if=axis_name_expr,
                        v_bind="props",
                    ):
                        v3.VRangeSlider(
                            v_if=f"{type_var} === 'range'",
                            prepend_icon=f"mdi-axis-{axis}-arrow",
                            v_model=(range_var, None),
                            min=(extents_min_expr,),
                            max=(extents_max_expr,),
                            step=1,
                            hide_details=True,
                            density="compact",
                            flat=True,
                            variant="solo",
                        )
                        v3.VSlider(
                            v_else=True,
                            prepend_icon=f"mdi-axis-{axis}-arrow",
                            v_model=(cut_var, 0),
                            min=(extents_min_expr,),
                            max=(extents_max_expr,),
                            step=1,
                            hide_details=True,
                            density="compact",
                            flat=True,
                            variant="solo",
                        )
                        v3.VCheckbox(
                            v_model=(type_var, "range"),
                            true_value="range",
                            false_value="cut",
                            true_icon="mdi-crop",
                            false_icon="mdi-box-cutter",
                            hide_details=True,
                            density="compact",
                            size="sm",
                            classes="mx-2",
                        )
