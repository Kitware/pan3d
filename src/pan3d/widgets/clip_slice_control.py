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
        ctx_name=None,  # Context name for programmatic access
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
            ctx_name: Context name for programmatic access (e.g., "clip_slice")
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

        # Initialize per-axis state variables as private instance variables
        # X axis
        self.__x_type = get_var(type_vars, 0, "x", "type")
        self.__x_range = get_var(range_vars, 0, "x", "range")
        self.__x_cut = get_var(cut_vars, 0, "x", "cut")
        self.__x_step = get_var(step_vars, 0, "x", "step")

        # Y axis
        self.__y_type = get_var(type_vars, 1, "y", "type")
        self.__y_range = get_var(range_vars, 1, "y", "range")
        self.__y_cut = get_var(cut_vars, 1, "y", "cut")
        self.__y_step = get_var(step_vars, 1, "y", "step")

        # Z axis
        self.__z_type = get_var(type_vars, 2, "z", "type")
        self.__z_range = get_var(range_vars, 2, "z", "range")
        self.__z_cut = get_var(cut_vars, 2, "z", "cut")
        self.__z_step = get_var(step_vars, 2, "z", "step")

        # Build UI
        with self:
            # X crop/cut
            with v3.VTooltip(
                v_if=f"{self.__axis_names}?.[0]",
                text=(
                    f"`${{{self.__axis_names}[0]}}: [${{{self.__dataset_bounds}[0]}}, ${{{self.__dataset_bounds}[1]}}] "
                    f"${{{self.__x_type} ==='range' ? "
                    f"('(' + {self.__x_range}.map((v,i) => v+1).concat({self.__x_step}).join(', ') + ')') : "
                    f"{self.__x_cut}}}`",
                ),
            ):
                with html.Template(v_slot_activator="{ props }"):
                    with html.Div(
                        classes="d-flex",
                        v_if=f"{self.__axis_names}?.[0]",
                        v_bind="props",
                    ):
                        v3.VRangeSlider(
                            v_if=f"{self.__x_type} === 'range'",
                            prepend_icon="mdi-axis-x-arrow",
                            v_model=(self.__x_range, None),
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
                            v_model=(self.__x_cut, 0),
                            min=(f"{self.__slice_extents}[{self.__axis_names}[0]][0]",),
                            max=(f"{self.__slice_extents}[{self.__axis_names}[0]][1]",),
                            step=1,
                            hide_details=True,
                            density="compact",
                            flat=True,
                            variant="solo",
                        )
                        v3.VCheckbox(
                            v_model=(self.__x_type, "range"),
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
                    f"${{{self.__y_type} ==='range' ? "
                    f"('(' + {self.__y_range}.map((v,i) => v+1).concat({self.__y_step}).join(', ') + ')') : "
                    f"{self.__y_cut}}}`",
                ),
            ):
                with html.Template(v_slot_activator="{ props }"):
                    with html.Div(
                        classes="d-flex",
                        v_if=f"{self.__axis_names}?.[1]",
                        v_bind="props",
                    ):
                        v3.VRangeSlider(
                            v_if=f"{self.__y_type} === 'range'",
                            prepend_icon="mdi-axis-y-arrow",
                            v_model=(self.__y_range, None),
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
                            v_model=(self.__y_cut, 0),
                            min=(f"{self.__slice_extents}[{self.__axis_names}[1]][0]",),
                            max=(f"{self.__slice_extents}[{self.__axis_names}[1]][1]",),
                            step=1,
                            hide_details=True,
                            density="compact",
                            flat=True,
                            variant="solo",
                        )
                        v3.VCheckbox(
                            v_model=(self.__y_type, "range"),
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
                    f"${{{self.__z_type} ==='range' ? "
                    f"('(' + {self.__z_range}.map((v,i) => v+1).concat({self.__z_step}).join(', ') + ')') : "
                    f"{self.__z_cut}}}`",
                ),
            ):
                with html.Template(v_slot_activator="{ props }"):
                    with html.Div(
                        classes="d-flex",
                        v_bind="props",
                        v_if=f"{self.__axis_names}?.[2]",
                    ):
                        v3.VRangeSlider(
                            v_if=f"{self.__z_type} === 'range'",
                            prepend_icon="mdi-axis-z-arrow",
                            v_model=(self.__z_range, None),
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
                            v_model=(self.__z_cut, 0),
                            min=(f"{self.__slice_extents}[{self.__axis_names}[2]][0]",),
                            max=(f"{self.__slice_extents}[{self.__axis_names}[2]][1]",),
                            step=1,
                            hide_details=True,
                            density="compact",
                            flat=True,
                            variant="solo",
                        )
                        v3.VCheckbox(
                            v_model=(self.__z_type, "range"),
                            true_value="range",
                            false_value="cut",
                            true_icon="mdi-crop",
                            false_icon="mdi-box-cutter",
                            hide_details=True,
                            density="compact",
                            size="sm",
                            classes="mx-2",
                        )

        # Register in context if ctx_name provided
        if ctx_name and hasattr(self, "ctx"):
            self.ctx[ctx_name] = self

    def set_axis_type(self, axis, type_value):
        """Set the type (range or cut) for a specific axis."""
        if axis == "x":
            self.state[self.__x_type] = type_value
        elif axis == "y":
            self.state[self.__y_type] = type_value
        elif axis == "z":
            self.state[self.__z_type] = type_value

    def set_axis_range(self, axis, range_value):
        """Set the range value for a specific axis."""
        if axis == "x":
            self.state[self.__x_range] = range_value
        elif axis == "y":
            self.state[self.__y_range] = range_value
        elif axis == "z":
            self.state[self.__z_range] = range_value

    def set_axis_cut(self, axis, cut_value):
        """Set the cut value for a specific axis."""
        if axis == "x":
            self.state[self.__x_cut] = cut_value
        elif axis == "y":
            self.state[self.__y_cut] = cut_value
        elif axis == "z":
            self.state[self.__z_cut] = cut_value

    def set_axis_step(self, axis, step_value):
        """Set the step value for a specific axis."""
        if axis == "x":
            self.state[self.__x_step] = step_value
        elif axis == "y":
            self.state[self.__y_step] = step_value
        elif axis == "z":
            self.state[self.__z_step] = step_value

    def update_slice_values(self, source, slices):
        """Update all slice values from source configuration."""
        from pan3d.utils.constants import XYZ

        for axis in XYZ:
            # default values
            axis_extent = self.state[self.__slice_extents].get(getattr(source, axis))
            self.set_axis_range(axis, axis_extent)
            self.set_axis_cut(axis, 0)
            self.set_axis_step(axis, 1)
            self.set_axis_type(axis, "range")

            # use slice info if available
            axis_slice = slices.get(getattr(source, axis))
            if axis_slice is not None:
                if isinstance(axis_slice, int):
                    # cut
                    self.set_axis_cut(axis, axis_slice)
                    self.set_axis_type(axis, "cut")
                else:
                    # range
                    self.set_axis_range(
                        axis, [axis_slice[0], axis_slice[1] - 1]
                    )  # end is inclusive
                    self.set_axis_step(axis, axis_slice[2])
