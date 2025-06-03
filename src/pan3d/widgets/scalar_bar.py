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

    def set_preset(self, preset_name):
        """Set the color preset for the scalar bar."""
        if preset_name not in PRESETS:
            err_msg = f"Preset '{preset_name}' not found."
            raise ValueError(err_msg)
        set_preset(self._lut, preset_name)
        self.state[self.__preset_key] = to_image(self._lut)

    def set_color_range(self, color_min, color_max):
        """Set the color range for the scalar bar."""
        self.state[self.__color_min_key] = color_min
        self.state[self.__color_max_key] = color_max
        # Update the lookup table range
        self._lut.SetRange(color_min, color_max)
        self.state[self.__preset_key] = to_image(self._lut)

    def __init__(self, preset=None, color_min=0.0, color_max=1.0, **kwargs):
        """Scalar bar for the XArray Explorers."""
        super().__init__(location="top")

        print("Updating the scalar bar")

        # Activate CSS
        self.server.enable_module(base)
        self.server.enable_module(vtk_view)

        __ns = kwargs.get("namespace", "view")
        if __ns == "view":
            ScalarBar._next_id += 1
            if ScalarBar._next_id > 1:
                __ns = f"view{ScalarBar._next_id}"

        self.__preset_key = f"{__ns}_preset"
        self.__color_min_key = f"{__ns}_color_min"
        self.__color_max_key = f"{__ns}_color_max"
        self.__scalarbar_probe_key = f"{__ns}_scalarbar_probe"
        self.__scalarbar_probe_key_available = f"{__ns}_scalarbar_probe_available"

        if preset is None:
            preset = next(iter(PRESETS.keys()))
        self._lut = vtkLookupTable()
        set_preset(self._lut, preset)

        # Initialize state
        self.state[self.__preset_key] = to_image(self._lut)
        self.state[self.__color_min_key] = color_min
        self.state[self.__color_max_key] = color_max

        self.state.setdefault(self.__scalarbar_probe_key, [])
        self.state.client_only(
            self.__scalarbar_probe_key, self.__scalarbar_probe_key_available
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
                        f"{{{{{self.__color_min_key}.toFixed(6) }}}}",
                        classes="scalarbar-left",
                    )
                    html.Img(
                        src=(self.__preset_key, None),
                        style="height: 100%; width: 100%;",
                        classes="rounded-lg border-thin",
                        mousemove=f"{self.__scalarbar_probe_key} = [$event.x, $event.target.getBoundingClientRect()]",
                        mouseenter=f"{self.__scalarbar_probe_key_available} = 1",
                        mouseleave=f"{self.__scalarbar_probe_key_available} = 0",
                        __events=["mousemove", "mouseenter", "mouseleave"],
                    )
                    html.Div(
                        v_show=(self.__scalarbar_probe_key_available, False),
                        classes="scalar-cursor",
                        style=(
                            f"`left: ${{{self.__scalarbar_probe_key}?.[0] - {self.__scalarbar_probe_key}?.[1]?.left}}px`",
                        ),
                    )
                    html.Div(
                        f"{{{{ {self.__color_max_key}.toFixed(6) }}}}",
                        classes="scalarbar-right",
                    )
            html.Span(
                f"{{{{ (({self.__color_max_key} - {self.__color_min_key}) * ({self.__scalarbar_probe_key}?.[0] - {self.__scalarbar_probe_key}?.[1]?.left) / {self.__scalarbar_probe_key}?.[1]?.width + {self.__color_min_key}).toFixed(6) }}}}"
            )
