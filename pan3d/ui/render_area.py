from trame.widgets import html, vuetify


class RenderArea(html.Div):
    def __init__(self, plot_view=None):
        super().__init__(
            v_show="array_active",
            style="height: 100%; position: relative; width: calc(100% - 300px)",
        )
        with self:
            vuetify.VBanner(
                "{{ error_message }}",
                v_show=("error_message",),
            )
            plot_view
