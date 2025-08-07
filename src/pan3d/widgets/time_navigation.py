"""Time Navigation widget for temporal data exploration."""

import math

from pan3d.ui.css import base, preview
from pan3d.utils.convert import max_str_length
from trame.widgets import html
from trame.widgets import vuetify3 as v3


class TimeNavigation(html.Div):
    """
    Presentation widget for navigating through time-based data.

    Provides:
    - Time slider with current position
    - Time labels display with tooltip
    - Index display (current/total)

    Usage:
        time_nav = TimeNavigation(
            labels=["2020-01-01", "2020-01-02", ...],
            index_name="slice_t",
            labels_name="t_labels"
        )
    """

    _next_id = 0

    def __init__(
        self,
        # State variable names (optional)
        index_name=None,
        labels_name=None,
        labels=None,
        **kwargs,
    ):
        """
        Create a time navigation widget.

        Parameters
        ----------
        index_name : str, optional
            State variable name for current index
        labels_name : str, optional
            State variable name for labels array
        labels : list, optional
            Initial list of time labels (strings)
        """
        super().__init__(**kwargs)

        # Activate CSS
        self.server.enable_module(base)
        self.server.enable_module(preview)

        # Generate unique namespace
        TimeNavigation._next_id += 1
        self._id = TimeNavigation._next_id
        ns = f"time_nav_{self._id}"

        # Initialize state variables
        self.__index = index_name or f"{ns}_index"
        self.__labels = labels_name or f"{ns}_labels"
        self.__max_index = f"{ns}_max_index"

        # Set default state
        self.state[self.__index] = 0
        self.state[self.__labels] = labels if labels is not None else []
        self.state[self.__max_index] = len(labels) - 1 if labels else 0

        # Build UI directly in __init__
        with self:
            with v3.VTooltip(
                v_if=f"{self.__max_index} > 0",
                text=(
                    f"`time: ${{{self.__labels}[{self.__index}]}} (${{{self.__index}+1}}/${{{self.__max_index}+1}})`",
                ),
            ):
                with html.Template(v_slot_activator="{ props }"):
                    with html.Div(
                        classes="d-flex pr-2",
                        v_bind="props",
                    ):
                        v3.VSlider(
                            prepend_icon="mdi-clock-outline",
                            v_model=(self.__index, 0),
                            min=0,
                            max=(self.__max_index, 0),
                            step=1,
                            hide_details=True,
                            density="compact",
                            flat=True,
                            variant="solo",
                        )

    @property
    def index(self):
        """Get the current time index."""
        return self.state[self.__index]

    @index.setter
    def index(self, value):
        """Set the current time index."""
        with self.state:
            # Ensure index is within valid range
            max_index = self.state[self.__max_index]
            self.state[self.__index] = max(0, min(int(value), max_index))

    @property
    def labels(self):
        """Get the time labels."""
        return self.state[self.__labels]

    @labels.setter
    def labels(self, value):
        """Set the time labels and update max index."""
        with self.state:
            self.state[self.__labels] = list(value) if value else []
            max_index = len(value) - 1 if value else 0
            self.state[self.__max_index] = max_index

            # Also set slice_t_max for backward compatibility
            self.state.slice_t_max = max_index

            # Calculate presentation-specific widths
            self.state.max_time_width = (
                math.ceil(0.58 * max_str_length(value)) if value else 0
            )
            if max_index > 0:
                self.state.max_time_index_width = math.ceil(
                    0.6 + (math.log10(max_index + 1) + 1) * 2 * 0.58
                )
            else:
                self.state.max_time_index_width = 0
