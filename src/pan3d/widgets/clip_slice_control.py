"""Clip/Slice Control widget for multi-axis data clipping and slicing."""

from trame.widgets import html
from trame.widgets import vuetify3 as v3


class ClipSliceControl(html.Div):
    """
    A widget for controlling clipping/cropping along all axes (X, Y, Z).

    Provides range selection or single cut value for data clipping on each axis.
    """

    _next_id = 0

    def __init__(
        self,
        # State variable names (optional)
        state_prefix=None,
        axis_names_var=None,
        dataset_bounds_var=None,
        slice_extents_var=None,
        # Optional lists/tuples for custom axis variable names [x, y, z]
        type_vars=None,  # e.g., ["slice_x_type", "slice_y_type", "slice_z_type"]
        range_vars=None,  # e.g., ["slice_x_range", "slice_y_range", "slice_z_range"]
        cut_vars=None,  # e.g., ["slice_x_cut", "slice_y_cut", "slice_z_cut"]
        step_vars=None,  # e.g., ["slice_x_step", "slice_y_step", "slice_z_step"]
        **kwargs,
    ):
        """
        Initialize the ClipSliceControl widget.

        Args:
            state_prefix: Prefix for state variable names. If not provided, generates unique prefix.
            axis_names_var: State variable for axis names array
            dataset_bounds_var: State variable for dataset bounds
            slice_extents_var: State variable for slice extents
            type_vars: Optional list/tuple of variable names for axis types [x, y, z]
            range_vars: Optional list/tuple of variable names for axis ranges [x, y, z]
            cut_vars: Optional list/tuple of variable names for axis cut values [x, y, z]
            step_vars: Optional list/tuple of variable names for axis steps [x, y, z]
            **kwargs: Additional div properties
        """
        super().__init__(**kwargs)

        # Generate unique namespace if not provided
        ClipSliceControl._next_id += 1
        self._id = ClipSliceControl._next_id
        ns = state_prefix or f"clip_slice_{self._id}"

        # Initialize shared state variables
        self.__axis_names = axis_names_var or f"{ns}_axis_names"
        self.__dataset_bounds = dataset_bounds_var or f"{ns}_dataset_bounds"
        self.__slice_extents = slice_extents_var or f"{ns}_slice_extents"

        # Helper function to get variable name from list or use default
        def get_var(var_list, index, axis, suffix):
            if var_list and len(var_list) > index:
                return var_list[index]
            return f"{ns}_slice_{axis}_{suffix}"

        # Initialize per-axis state variables
        axes = ["x", "y", "z"]
        self._axis_vars = {}

        for i, axis in enumerate(axes):
            self._axis_vars[axis] = {
                "type": get_var(type_vars, i, axis, "type"),
                "range": get_var(range_vars, i, axis, "range"),
                "cut": get_var(cut_vars, i, axis, "cut"),
                "step": get_var(step_vars, i, axis, "step"),
                "index": i,
            }

        # Build UI
        with self:
            # X crop/cut
            with v3.VTooltip(
                v_if=f"{self.__axis_names}?.[0]",
                text=(
                    f"`${{{self.__axis_names}[0]}}: [${{{self.__dataset_bounds}[0]}}, ${{{self.__dataset_bounds}[1]}}] "
                    f"${{{self._axis_vars['x']['type']} ==='range' ? "
                    f"('(' + {self._axis_vars['x']['range']}.map((v,i) => v+1).concat({self._axis_vars['x']['step']}).join(', ') + ')') : "
                    f"{self._axis_vars['x']['cut']}}}`",
                ),
            ):
                with html.Template(v_slot_activator="{ props }"):
                    with html.Div(
                        classes="d-flex",
                        v_if=f"{self.__axis_names}?.[0]",
                        v_bind="props",
                    ):
                        v3.VRangeSlider(
                            v_if=f"{self._axis_vars['x']['type']} === 'range'",
                            prepend_icon="mdi-axis-x-arrow",
                            v_model=(self._axis_vars["x"]["range"], None),
                            min=(f"{self.__slice_extents}[{self.__axis_names}[0]][0]",),
                            max=(f"{self.__slice_extents}[{self.__axis_names}[0]][1]",),
                            step=1,
                            hide_details=True,
                            density="compact",
                            flat=True,
                            variant="solo",
                        )
                        v3.VSlider(
                            v_else=True,
                            prepend_icon="mdi-axis-x-arrow",
                            v_model=(self._axis_vars["x"]["cut"], 0),
                            min=(f"{self.__slice_extents}[{self.__axis_names}[0]][0]",),
                            max=(f"{self.__slice_extents}[{self.__axis_names}[0]][1]",),
                            step=1,
                            hide_details=True,
                            density="compact",
                            flat=True,
                            variant="solo",
                        )
                        v3.VCheckbox(
                            v_model=(self._axis_vars["x"]["type"], "range"),
                            true_value="range",
                            false_value="cut",
                            true_icon="mdi-crop",
                            false_icon="mdi-box-cutter",
                            hide_details=True,
                            density="compact",
                            size="sm",
                            classes="mx-2",
                        )

            # Y crop/cut
            with v3.VTooltip(
                v_if=f"{self.__axis_names}?.[1]",
                text=(
                    f"`${{{self.__axis_names}[1]}}: [${{{self.__dataset_bounds}[2]}}, ${{{self.__dataset_bounds}[3]}}] "
                    f"${{{self._axis_vars['y']['type']} ==='range' ? "
                    f"('(' + {self._axis_vars['y']['range']}.map((v,i) => v+1).concat({self._axis_vars['y']['step']}).join(', ') + ')') : "
                    f"{self._axis_vars['y']['cut']}}}`",
                ),
            ):
                with html.Template(v_slot_activator="{ props }"):
                    with html.Div(
                        classes="d-flex",
                        v_if=f"{self.__axis_names}?.[1]",
                        v_bind="props",
                    ):
                        v3.VRangeSlider(
                            v_if=f"{self._axis_vars['y']['type']} === 'range'",
                            prepend_icon="mdi-axis-y-arrow",
                            v_model=(self._axis_vars["y"]["range"], None),
                            min=(f"{self.__slice_extents}[{self.__axis_names}[1]][0]",),
                            max=(f"{self.__slice_extents}[{self.__axis_names}[1]][1]",),
                            step=1,
                            hide_details=True,
                            density="compact",
                            flat=True,
                            variant="solo",
                        )
                        v3.VSlider(
                            v_else=True,
                            prepend_icon="mdi-axis-y-arrow",
                            v_model=(self._axis_vars["y"]["cut"], 0),
                            min=(f"{self.__slice_extents}[{self.__axis_names}[1]][0]",),
                            max=(f"{self.__slice_extents}[{self.__axis_names}[1]][1]",),
                            step=1,
                            hide_details=True,
                            density="compact",
                            flat=True,
                            variant="solo",
                        )
                        v3.VCheckbox(
                            v_model=(self._axis_vars["y"]["type"], "range"),
                            true_value="range",
                            false_value="cut",
                            true_icon="mdi-crop",
                            false_icon="mdi-box-cutter",
                            hide_details=True,
                            density="compact",
                            size="sm",
                            classes="mx-2",
                        )

            # Z crop/cut
            with v3.VTooltip(
                v_if=f"{self.__axis_names}?.[2]",
                text=(
                    f"`${{{self.__axis_names}[2]}}: [${{{self.__dataset_bounds}[4]}}, ${{{self.__dataset_bounds}[5]}}] "
                    f"${{{self._axis_vars['z']['type']} ==='range' ? "
                    f"('(' + {self._axis_vars['z']['range']}.map((v,i) => v+1).concat({self._axis_vars['z']['step']}).join(', ') + ')') : "
                    f"{self._axis_vars['z']['cut']}}}`",
                ),
            ):
                with html.Template(v_slot_activator="{ props }"):
                    with html.Div(
                        classes="d-flex",
                        v_bind="props",
                        v_if=f"{self.__axis_names}?.[2]",
                    ):
                        v3.VRangeSlider(
                            v_if=f"{self._axis_vars['z']['type']} === 'range'",
                            prepend_icon="mdi-axis-z-arrow",
                            v_model=(self._axis_vars["z"]["range"], None),
                            min=(f"{self.__slice_extents}[{self.__axis_names}[2]][0]",),
                            max=(f"{self.__slice_extents}[{self.__axis_names}[2]][1]",),
                            step=1,
                            hide_details=True,
                            density="compact",
                            flat=True,
                            variant="solo",
                        )
                        v3.VSlider(
                            v_else=True,
                            prepend_icon="mdi-axis-z-arrow",
                            v_model=(self._axis_vars["z"]["cut"], 0),
                            min=(f"{self.__slice_extents}[{self.__axis_names}[2]][0]",),
                            max=(f"{self.__slice_extents}[{self.__axis_names}[2]][1]",),
                            step=1,
                            hide_details=True,
                            density="compact",
                            flat=True,
                            variant="solo",
                        )
                        v3.VCheckbox(
                            v_model=(self._axis_vars["z"]["type"], "range"),
                            true_value="range",
                            false_value="cut",
                            true_icon="mdi-crop",
                            false_icon="mdi-box-cutter",
                            hide_details=True,
                            density="compact",
                            size="sm",
                            classes="mx-2",
                        )
