"""Slice Control widget for single-axis slicing operations."""

from trame.widgets import html
from trame.widgets import vuetify3 as v3


class SliceControl(html.Div):
    """
    A widget for controlling slicing along selectable axes.

    Provides axis selection and position control for slice exploration.
    """

    _next_id = 0

    def __init__(
        self,
        # State variable names (optional)
        state_prefix=None,
        slice_axis_var=None,
        axis_names_var=None,
        cut_x_var=None,
        cut_y_var=None,
        cut_z_var=None,
        bounds_var=None,
        # UI options
        show_value_display=True,
        show_bounds=True,
        **kwargs,
    ):
        """
        Initialize the SliceControl widget.

        Args:
            state_prefix: Prefix for state variable names. If not provided, generates unique prefix.
            slice_axis_var: State variable for selected axis (default: {prefix}_slice_axis)
            axis_names_var: State variable for axis names array (default: {prefix}_axis_names)
            cut_x_var: State variable for X cut position (default: {prefix}_cut_x)
            cut_y_var: State variable for Y cut position (default: {prefix}_cut_y)
            cut_z_var: State variable for Z cut position (default: {prefix}_cut_z)
            bounds_var: State variable for bounds array (default: {prefix}_bounds)
            show_value_display: Whether to show current value
            show_bounds: Whether to show min/max bounds
            **kwargs: Additional div properties
        """
        super().__init__(**kwargs)

        # Generate unique namespace if not provided
        SliceControl._next_id += 1
        self._id = SliceControl._next_id
        ns = state_prefix or f"slice_control_{self._id}"

        # Initialize state variable names as private instance variables
        self.__slice_axis = slice_axis_var or f"{ns}_slice_axis"
        self.__axis_names = axis_names_var or f"{ns}_axis_names"
        self.__cut_x = cut_x_var or f"{ns}_cut_x"
        self.__cut_y = cut_y_var or f"{ns}_cut_y"
        self.__cut_z = cut_z_var or f"{ns}_cut_z"
        self.__bounds = bounds_var or f"{ns}_bounds"

        # Note: State initialization must be done by the parent explorer/viewer
        # Widgets don't have access to state during construction

        style = {
            "hide_details": True,
            "density": "compact",
            "flat": True,
            "variant": "solo",
        }

        with self:
            # Value display
            if show_value_display:
                with html.Div(classes="d-flex align-center justify-center mb-2"):
                    html.Span(
                        f"{{{{parseFloat({self.__cut_x}).toFixed(2)}}}}",
                        v_show=f"{self.__slice_axis} === {self.__axis_names}[0]",
                        classes="text-subtitle-1",
                    )
                    html.Span(
                        f"{{{{parseFloat({self.__cut_y}).toFixed(2)}}}}",
                        v_show=f"{self.__slice_axis} === {self.__axis_names}[1]",
                        classes="text-subtitle-1",
                    )
                    html.Span(
                        f"{{{{parseFloat({self.__cut_z}).toFixed(2)}}}}",
                        v_show=f"{self.__slice_axis} === {self.__axis_names}[2]",
                        classes="text-subtitle-1",
                    )

            # Axis selector
            with v3.VRow(classes="mx-2 my-0"):
                v3.VSelect(
                    v_model=(self.__slice_axis,),
                    items=(self.__axis_names,),
                    **style,
                )

            # Sliders for each axis
            with v3.VRow(classes="mx-2 my-0"):
                v3.VSlider(
                    v_show=f"{self.__slice_axis} === {self.__axis_names}[0]",
                    v_model=(self.__cut_x,),
                    min=(f"{self.__bounds}[0]",),
                    max=(f"{self.__bounds}[1]",),
                    **style,
                )
                v3.VSlider(
                    v_show=f"{self.__slice_axis} === {self.__axis_names}[1]",
                    v_model=(self.__cut_y,),
                    min=(f"{self.__bounds}[2]",),
                    max=(f"{self.__bounds}[3]",),
                    **style,
                )
                v3.VSlider(
                    v_show=f"{self.__slice_axis} === {self.__axis_names}[2]",
                    v_model=(self.__cut_z,),
                    min=(f"{self.__bounds}[4]",),
                    max=(f"{self.__bounds}[5]",),
                    **style,
                )

            # Bounds display
            if show_bounds:
                with v3.VRow(classes="mx-2 my-0"):
                    with v3.VCol():
                        html.Div(
                            f"{{{{parseFloat({self.__bounds}[{self.__axis_names}.indexOf({self.__slice_axis})*2]).toFixed(2)}}}}",
                            classes="font-weight-medium",
                        )
                    with v3.VCol(classes="text-right"):
                        html.Div(
                            f"{{{{parseFloat({self.__bounds}[{self.__axis_names}.indexOf({self.__slice_axis})*2 + 1]).toFixed(2)}}}}",
                            classes="font-weight-medium",
                        )
