"""Error Alert widget for consistent error display across explorers."""

from trame.widgets import html
from trame.widgets import vuetify3 as v3


class ErrorAlert(v3.VAlert):
    """
    A reusable error alert component.

    Provides consistent error display across all explorers.
    """

    def __init__(
        self,
        error_key="data_origin_error",
        title="Error",
        position="fixed",
        location="bottom",
        max_width=650,
        type="error",
        **kwargs,
    ):
        """
        Initialize the ErrorAlert widget.

        Args:
            error_key: State key for error message
            title: Alert title
            position: CSS position (fixed, absolute, etc.)
            location: Vuetify location (bottom, top, etc.)
            max_width: Maximum width of alert
            type: Alert type (error, warning, info, success)
            **kwargs: Additional VAlert properties
        """
        super().__init__(
            v_model=(error_key, False),
            position=position,
            location=location,
            max_width=max_width,
            type=type,
            closable=True,
            border="start",
            **kwargs,
        )

        with self:
            with v3.VAlertTitle():
                v3.VIcon("mdi-alert-circle", classes="mr-2")
                html.Span(title, classes="text-h6")
            html.Div(f"{{{{ {error_key} }}}}", classes="text-body-2 mt-2")
