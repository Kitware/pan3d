"""Level of Detail control widget for slice stepping."""

from trame.widgets import html
from trame.widgets import vuetify3 as v3


class LevelOfDetail(html.Div):
    """
    A widget for controlling level of detail/slice stepping.

    Provides step controls for X, Y, Z axes.
    """

    _next_id = 0

    def __init__(
        self,
        # State variable names (optional)
        state_prefix=None,
        step_x_name=None,
        step_y_name=None,
        step_z_name=None,
        axis_names_var=None,
        # UI options
        min_value=1,
        **kwargs,
    ):
        """
        Initialize the LevelOfDetail widget.

        Args:
            state_prefix: Prefix for state variable names. If not provided, generates unique prefix.
            step_x_name: State variable name for X step (default: {prefix}_step_x)
            step_y_name: State variable name for Y step (default: {prefix}_step_y)
            step_z_name: State variable name for Z step (default: {prefix}_step_z)
            axis_names_var: State variable containing axis names array (default: {prefix}_axis_names)
            min_value: Minimum step value
            **kwargs: Additional div properties
        """
        super().__init__(**kwargs)

        # Generate unique namespace if not provided
        LevelOfDetail._next_id += 1
        self._id = LevelOfDetail._next_id
        ns = state_prefix or f"level_of_detail_{self._id}"

        # Initialize state variable names
        self._state_vars = {
            "step_x": step_x_name or f"{ns}_step_x",
            "step_y": step_y_name or f"{ns}_step_y",
            "step_z": step_z_name or f"{ns}_step_z",
            "axis_names": axis_names_var or f"{ns}_axis_names",
        }

        # Use provided variables or defaults for backward compatibility
        step_x_name = step_x_name or "slice_x_step"
        step_y_name = step_y_name or "slice_y_step"
        step_z_name = step_z_name or "slice_z_step"
        axis_names_var = axis_names_var or "axis_names"

        with self:
            with v3.VTooltip(text="Level Of Details / Slice stepping"):
                with html.Template(v_slot_activator="{ props }"):
                    with v3.VRow(
                        v_bind="props",
                        no_gutters=True,
                        classes="align-center my-0 mx-0 border-b-thin",
                    ):
                        v3.VIcon(
                            "mdi-stairs",
                            classes="ml-2 text-medium-emphasis",
                        )
                        with v3.VCol(classes="pa-0", v_if=f"{axis_names_var}?.[0]"):
                            v3.VTextField(
                                v_model_number=(step_x_name, 1),
                                hide_details=True,
                                density="compact",
                                flat=True,
                                variant="solo",
                                reverse=True,
                                raw_attrs=[f'min="{min_value}"'],
                                type="number",
                            )
                        with v3.VCol(classes="pa-0", v_if=f"{axis_names_var}?.[1]"):
                            v3.VTextField(
                                v_model_number=(step_y_name, 1),
                                hide_details=True,
                                density="compact",
                                flat=True,
                                variant="solo",
                                reverse=True,
                                raw_attrs=[f'min="{min_value}"'],
                                type="number",
                            )
                        with v3.VCol(classes="pa-0", v_if=f"{axis_names_var}?.[2]"):
                            v3.VTextField(
                                v_model_number=(step_z_name, 1),
                                hide_details=True,
                                density="compact",
                                flat=True,
                                variant="solo",
                                reverse=True,
                                raw_attrs=[f'min="{min_value}"'],
                                type="number",
                            )
