"""Generic Vector Property Control widget for X, Y, Z properties."""

from trame.widgets import html
from trame.widgets import vuetify3 as v3


class VectorPropertyControl(html.Div):
    """
    A generic widget for controlling X, Y, Z vector properties.

    Can be used for scale, step, position, or any other 3D vector property.
    """

    _next_id = 0

    def __init__(
        self,
        # Property configuration
        property_name="property",
        icon="mdi-axis-arrow",
        tooltip="Vector property",
        # State variable names (optional)
        state_prefix=None,
        x_name=None,
        y_name=None,
        z_name=None,
        axis_names_var=None,
        # Value configuration
        default_value=1,
        min_value=None,
        max_value=None,
        step=None,
        use_number_model=True,  # Default to v_model_number for numeric values
        **kwargs,
    ):
        """
        Initialize the VectorPropertyControl widget.

        Args:
            property_name: Base name for the property (e.g., "scale", "step")
            icon: Material Design Icon name to display
            tooltip: Tooltip text to show on hover
            state_prefix: Prefix for state variable names. If not provided, generates unique prefix.
            x_name: State variable name for X component (default: {prefix}_{property_name}_x)
            y_name: State variable name for Y component (default: {prefix}_{property_name}_y)
            z_name: State variable name for Z component (default: {prefix}_{property_name}_z)
            axis_names_var: State variable name for axis names array (default: {prefix}_axis_names)
            default_value: Default value for all components
            min_value: Minimum allowed value
            max_value: Maximum allowed value
            step: Step increment for number inputs
            use_number_model: If True, uses v_model_number; if False, uses v_model (default: True)
            **kwargs: Additional div properties
        """
        super().__init__(**kwargs)

        # Generate unique namespace if not provided
        VectorPropertyControl._next_id += 1
        self._id = VectorPropertyControl._next_id
        ns = state_prefix or f"{property_name}_control_{self._id}"

        # Initialize state variable names as private instance variables
        self.__x = x_name or f"{ns}_{property_name}_x"
        self.__y = y_name or f"{ns}_{property_name}_y"
        self.__z = z_name or f"{ns}_{property_name}_z"
        self.__axis_names = axis_names_var or f"{ns}_axis_names"

        # Build raw attributes for input validation
        raw_attrs = []
        if min_value is not None:
            raw_attrs.append(f'min="{min_value}"')
        if max_value is not None:
            raw_attrs.append(f'max="{max_value}"')
        if step is not None:
            raw_attrs.append(f'step="{step}"')

        # Determine which v_model to use
        v_model_attr = "v_model_number" if use_number_model else "v_model"

        with self:
            with v3.VTooltip(text=tooltip):
                with html.Template(v_slot_activator="{ props }"):
                    with v3.VRow(
                        v_bind="props",
                        no_gutters=bool(use_number_model),
                        classes="align-center my-0 mx-0 border-b-thin",
                    ):
                        v3.VIcon(
                            icon,
                            classes="ml-2 text-medium-emphasis",
                        )
                        # X component
                        with v3.VCol(classes="pa-0", v_if=f"{self.__axis_names}?.[0]"):
                            v3.VTextField(
                                **{v_model_attr: (self.__x, default_value)},
                                hide_details=True,
                                density="compact",
                                flat=True,
                                variant="solo",
                                reverse=True,
                                raw_attrs=raw_attrs if raw_attrs else None,
                                type="number",
                            )
                        # Y component
                        with v3.VCol(classes="pa-0", v_if=f"{self.__axis_names}?.[1]"):
                            v3.VTextField(
                                **{v_model_attr: (self.__y, default_value)},
                                hide_details=True,
                                density="compact",
                                flat=True,
                                variant="solo",
                                reverse=True,
                                raw_attrs=raw_attrs if raw_attrs else None,
                                type="number",
                            )
                        # Z component
                        with v3.VCol(classes="pa-0", v_if=f"{self.__axis_names}?.[2]"):
                            v3.VTextField(
                                **{v_model_attr: (self.__z, default_value)},
                                hide_details=True,
                                density="compact",
                                flat=True,
                                variant="solo",
                                reverse=True,
                                raw_attrs=raw_attrs if raw_attrs else None,
                                type="number",
                            )

    @property
    def x_var(self):
        """Get the X component state variable name."""
        return self.__x

    @property
    def y_var(self):
        """Get the Y component state variable name."""
        return self.__y

    @property
    def z_var(self):
        """Get the Z component state variable name."""
        return self.__z

    @property
    def axis_names_var(self):
        """Get the axis names state variable name."""
        return self.__axis_names
