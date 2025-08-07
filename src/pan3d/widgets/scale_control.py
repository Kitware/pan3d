"""Scale Control widget for axis scaling."""

from trame.widgets import html
from trame.widgets import vuetify3 as v3


class ScaleControl(html.Div):
    """
    A widget for controlling X, Y, Z scale factors.

    Provides unified scale controls with validation.
    """

    _next_id = 0

    def __init__(
        self,
        # State variable names (optional)
        state_prefix=None,
        scale_x_name=None,
        scale_y_name=None,
        scale_z_name=None,
        axis_names_var=None,
        # UI options
        min_value=0.01,
        max_value=100,
        step=0.1,
        density="compact",
        **kwargs,
    ):
        """
        Initialize the ScaleControl widget.

        Args:
            state_prefix: Prefix for state variable names. If not provided, generates unique prefix.
            scale_x_name: State variable name for X scale (default: {prefix}_scale_x)
            scale_y_name: State variable name for Y scale (default: {prefix}_scale_y)
            scale_z_name: State variable name for Z scale (default: {prefix}_scale_z)
            axis_names_var: State variable name for axis names array (default: {prefix}_axis_names)
            min_value: Minimum scale value
            max_value: Maximum scale value
            step: Scale step increment
            density: Vuetify density setting
            **kwargs: Additional div properties
        """
        super().__init__(**kwargs)

        # Generate unique namespace if not provided
        ScaleControl._next_id += 1
        self._id = ScaleControl._next_id
        ns = state_prefix or f"scale_control_{self._id}"

        # Initialize state variable names as private instance variables
        self.__scale_x = scale_x_name or f"{ns}_scale_x"
        self.__scale_y = scale_y_name or f"{ns}_scale_y"
        self.__scale_z = scale_z_name or f"{ns}_scale_z"
        self.__axis_names = axis_names_var or f"{ns}_axis_names"

        with self:
            # Actor scaling
            with v3.VTooltip(text="Representation scaling"):
                with html.Template(v_slot_activator="{ props }"):
                    with v3.VRow(
                        v_bind="props",
                        no_gutter=True,
                        classes="align-center my-0 mx-0 border-b-thin",
                    ):
                        v3.VIcon(
                            "mdi-ruler-square",
                            classes="ml-2 text-medium-emphasis",
                        )
                        with v3.VCol(classes="pa-0", v_if=f"{self.__axis_names}?.[0]"):
                            v3.VTextField(
                                v_model=(self.__scale_x, 1),
                                hide_details=True,
                                density="compact",
                                flat=True,
                                variant="solo",
                                reverse=True,
                                raw_attrs=[
                                    'pattern="^\d*(\.\d)?$"',
                                    'min="0.001"',
                                    'step="0.1"',
                                ],
                                type="number",
                            )
                        with v3.VCol(classes="pa-0", v_if=f"{self.__axis_names}?.[1]"):
                            v3.VTextField(
                                v_model=(self.__scale_y, 1),
                                hide_details=True,
                                density="compact",
                                flat=True,
                                variant="solo",
                                reverse=True,
                                raw_attrs=[
                                    'pattern="^\d*(\.\d)?$"',
                                    'min="0.001"',
                                    'step="0.1"',
                                ],
                                type="number",
                            )
                        with v3.VCol(classes="pa-0", v_if=f"{self.__axis_names}?.[2]"):
                            v3.VTextField(
                                v_model=(self.__scale_z, 1),
                                hide_details=True,
                                density="compact",
                                flat=True,
                                variant="solo",
                                reverse=True,
                                raw_attrs=[
                                    'pattern="^\d*(\.\d)?$"',
                                    'min="0.001"',
                                    'step="0.1"',
                                ],
                                type="number",
                            )
