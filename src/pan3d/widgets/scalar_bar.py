from vtkmodules.vtkCommonCore import vtkLookupTable

from pan3d.ui.css import base, vtk_view
from pan3d.utils.convert import to_image
from pan3d.utils.presets import PRESETS, set_preset
from trame.widgets import html
from trame.widgets import vuetify3 as v3


class ScalarBar(v3.VTooltip):
    """
    Scalar bar for the XArray Explorers.
    """

    _next_id = 0

    @classmethod
    def next_id(cls):
        """Get the next unique ID for the scalar bar."""
        cls._next_id += 1
        return f"pan3d_scalarbar{cls._next_id}"

    def __init__(
        self, preset="Fast", color_min=0.0, color_max=1.0, ctx_name=None, **kwargs
    ):
        """Scalar bar for the XArray Explorers."""
        self._lut = vtkLookupTable()
        super().__init__(location="top", ctx_name=ctx_name)
        # Activate CSS
        self.server.enable_module(base)
        self.server.enable_module(vtk_view)

        ns = self.next_id()
        self.__preset_image = f"{ns}_preset"
        self.__color_min = f"{ns}_color_min"
        self.__color_max = f"{ns}_color_max"
        # Probe enables mouse events for scalar bar
        self.__probe_location = f"{ns}_probe_location"
        self.__probe_enabled = f"{ns}_probe_enabled"

        # Initialize state
        self.preset = preset
        self.set_color_range(color_min, color_max)
        self.state[self.__probe_location] = []
        self.state[self.__probe_enabled] = 0
        self.state.client_only(
            self.__probe_location,
            self.__probe_enabled,
        )

        with self:
            # Content
            with html.Template(v_slot_activator="{ props }"):
                with html.Div(
                    classes="scalarbar",
                    rounded="pill",
                    v_bind="props",
                    **kwargs,
                ):
                    html.Div(
                        f"{{{{{self.__color_min}.toFixed(6) }}}}",
                        classes="scalarbar-left",
                    )
                    html.Img(
                        src=(self.__preset_image, None),
                        style="height: 100%; width: 100%;",
                        classes="rounded-lg border-thin",
                        mousemove=f"{self.__probe_location} = [$event.x, $event.target.getBoundingClientRect()]",
                        mouseenter=f"{self.__probe_enabled} = 1",
                        mouseleave=f"{self.__probe_enabled} = 0",
                        __events=["mousemove", "mouseenter", "mouseleave"],
                    )
                    html.Div(
                        v_show=(self.__probe_enabled, False),
                        classes="scalar-cursor",
                        style=(
                            f"`left: ${{{self.__probe_location}?.[0] - {self.__probe_location}?.[1]?.left}}px`",
                        ),
                    )
                    html.Div(
                        f"{{{{ {self.__color_max}.toFixed(6) }}}}",
                        classes="scalarbar-right",
                    )
            html.Span(
                f"{{{{ (({self.__color_max} - {self.__color_min}) * ({self.__probe_location}?.[0] - {self.__probe_location}?.[1]?.left) / {self.__probe_location}?.[1]?.width + {self.__color_min}).toFixed(6) }}}}"
            )

    @property
    def preset(self):
        return self._preset

    @preset.setter
    def preset(self, value):
        if value not in PRESETS:
            err_msg = f"Preset '{value}' not found."
            raise ValueError(err_msg)
        self._preset = value
        set_preset(self._lut, value)
        with self.state:
            self.state[self.__preset_image] = to_image(self._lut)

    @property
    def preset_image_name(self):
        return self.__preset_image

    @property
    def color_min(self):
        return self.state[self.__color_min]

    @color_min.setter
    def color_min(self, value):
        with self.state:
            self.state[self.__color_min] = value

    @property
    def color_min_name(self):
        return self.__color_min

    @property
    def color_max(self):
        return self.state[self.__color_max]

    @color_max.setter
    def color_max(self, value):
        with self.state:
            self.state[self.__color_max] = value

    @property
    def color_max_name(self):
        return self.__color_max

    def set_color_range(self, color_min, color_max):
        """Set the color range for the scalar bar."""
        self.state[self.__color_min] = color_min
        self.state[self.__color_max] = color_max
