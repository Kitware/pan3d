from vtkmodules.vtkCommonCore import vtkLookupTable
from vtkmodules.vtkRenderingCore import vtkMapper

from pan3d.ui.css import base, vtk_view
from pan3d.utils.convert import to_image
from pan3d.utils.presets import PRESETS, set_preset
from trame.widgets import html
from trame.widgets import vuetify3 as v3


class ColorBy(html.Div):
    """Color settings for the XArray Explorers.
    Arguments:
        source: The source of the data to be colored.
        color_by: The name of the data array to color by.
        data_arrays: The list of available data arrays.
        color_min: The minimum value for the color range.
        color_max: The maximum value for the color range.
        nan_color: The color to use for NaN values.
        color_preset: The name of the color preset to use.
        color_presets: The list of available color presets.
    """

    def __init__(
        self,
        retrieve_source=None,
        retrieve_mapper=None,
        color_by="color_by",
        data_arrays="data_arrays",
        color_min="color_min",
        color_max="color_max",
        nan_color="nan_color",
        color_preset="color_preset",
        color_presets="color_presets",
        preset_img="preset_img",
        **kwargs,
    ):
        super().__init__(**kwargs)

        self.lut = vtkLookupTable()

        # initialize component specific variables
        self._retrieve_source = retrieve_source
        self._retrieve_mapper = retrieve_mapper
        self._color_by = color_by
        self._data_arrays = data_arrays
        self._color_min = color_min
        self._color_max = color_max
        self._nan_color = nan_color
        self._color_preset = color_preset
        self._color_presets = color_presets
        self._preset_img = preset_img

        # Track state changes
        self.state.change(data_arrays)(self._on_change_data_arrays)
        self.state.change(color_by)(self._on_change_color_by)
        self.state.change(color_min, color_max, color_preset, nan_color)(
            self._on_change_properties
        )

        with self:
            v3.VSelect(
                placeholder="Color By",
                prepend_inner_icon="mdi-format-color-fill",
                v_model=(color_by, None),
                items=(data_arrays, []),
                clearable=True,
                hide_details=True,
                density="compact",
                flat=True,
                variant="solo",
            )
            v3.VDivider()
            with v3.VRow(no_gutters=True, classes="align-center mr-0"):
                with v3.VCol():
                    v3.VTextField(
                        prepend_inner_icon="mdi-water-minus",
                        v_model_number=(color_min, 0.45),
                        type="number",
                        hide_details=True,
                        density="compact",
                        flat=True,
                        variant="solo",
                        reverse=True,
                    )
                with v3.VCol():
                    v3.VTextField(
                        prepend_inner_icon="mdi-water-plus",
                        v_model_number=(color_max, 5.45),
                        type="number",
                        hide_details=True,
                        density="compact",
                        flat=True,
                        variant="solo",
                        reverse=True,
                    )
                with html.Div(classes="flex-0"):
                    v3.VBtn(
                        icon="mdi-arrow-split-vertical",
                        size="sm",
                        density="compact",
                        flat=True,
                        variant="outlined",
                        classes="mx-2",
                        click=self.reset_color_range,
                    )
            # v3.VDivider()
            with html.Div(classes="mx-2"):
                html.Img(
                    src=("preset_img", None),
                    style="height: 0.75rem; width: 100%;",
                    classes="rounded-lg border-thin",
                )
            v3.VSelect(
                placeholder="Color Preset",
                prepend_inner_icon="mdi-palette",
                v_model=(color_preset, "Fast"),
                items=(color_presets, list(PRESETS.keys())),
                hide_details=True,
                density="compact",
                flat=True,
                variant="solo",
            )

            with v3.VTooltip(
                text=("`NaN Color (${nan_colors[nan_color]})`",),
            ):
                with html.Template(v_slot_activator="{ props }"):
                    with v3.VItemGroup(
                        v_model=nan_color,
                        v_bind="props",
                        classes="d-inline-flex ga-1 pa-2",
                        mandatory="force",
                    ):
                        v3.VIcon(
                            "mdi-eyedropper-variant",
                            classes="my-auto mx-1 text-medium-emphasis",
                        )
                        with v3.VItem(
                            v_for="(color, i) in nan_colors", key="i", value=("i",)
                        ):
                            with v3.Template(
                                raw_attrs=['#default="{ isSelected, toggle }"']
                            ):
                                with v3.VAvatar(
                                    density="compact",
                                    color=("isSelected ? 'primary': 'transparent'",),
                                ):
                                    v3.VBtn(
                                        "{{ color[3] < 0.1 ? 't' : '' }}",
                                        density="compact",
                                        border="md surface opacity-100",
                                        color=(
                                            "color[3] ? `rgb(${color[0] * 255}, ${color[1] * 255}, ${color[2] * 255})` : undefined",
                                        ),
                                        flat=True,
                                        icon=True,
                                        ripple=False,
                                        size="small",
                                        click="toggle",
                                    )

    def _on_change_data_arrays(self, **__):
        state = self.state
        data_arrays = self.state[self._data_arrays]
        color_by = state[self._color_by]
        if len(data_arrays) == 0:
            state[self._color_by] = None
        elif color_by is None or color_by not in data_arrays:
            state[self._color_by] = data_arrays[0]

    def _on_change_color_by(self, **__):
        state = self.state
        source = self._retrieve_source()
        mapper: vtkMapper = self._retrieve_mapper()

        if source is None:
            return

        color_by = state[self._color_by]

        ds = source()
        if color_by in ds.point_data.keys():  # vtk is missing in iter
            array = ds.point_data[color_by]
            min_value, max_value = array.GetRange()

            state[self._color_min] = min_value
            state[self._color_max] = max_value

            if mapper is not None:
                mapper.SetLookupTable(self.lut)
                mapper.SelectColorArray(color_by)
                mapper.SetScalarModeToUsePointFieldData()
                mapper.InterpolateScalarsBeforeMappingOn()
                mapper.SetScalarVisibility(1)
        else:
            if mapper is not None:
                mapper.SetScalarVisibility(0)
            state[self._color_min] = 0
            state[self._color_max] = 1

    def _on_change_properties(self, **__):
        """Change the color properties based on the selected data array,preset and range"""
        state = self.state
        mapper: vtkMapper = self._retrieve_mapper()

        color_min = state[self._color_min]
        color_max = state[self._color_max]
        color_min = float(color_min)
        color_max = float(color_max)
        if mapper is not None:
            mapper.SetLookupTable(self.lut)
            mapper.SetScalarRange(color_min, color_max)

        nan_colors = state.nan_colors
        nan_color = state[self._nan_color]
        color = nan_colors[nan_color]
        self.lut.SetNanColor(color)

        preset = state[self._color_preset]
        set_preset(self.lut, preset)
        state.preset_img = to_image(self.lut, 255)

        self.ctrl.view_update()

    def reset_color_range(self):
        """Reset the color range to the min and max values of the selected data array."""
        state = self.state
        color_by = state[self._color_by]
        source = self._retrieve_source()
        ds = source()

        if color_by in ds.point_data.keys():  # vtk is missing in iter
            array = ds.point_data[color_by]
            min_value, max_value = array.GetRange()

            state[self._color_min] = min_value
            state[self._color_max] = max_value
        else:
            state[self._color_min] = 0
            state[self._color_max] = 1

        self.ctrl.view_update()


class ScalarBar(v3.VTooltip):
    def __init__(self, img_src, color_min="color_min", color_max="color_max", **kwargs):
        """Scalar bar for the XArray Explorers."""
        super().__init__(location="top")

        # Activate CSS
        self.server.enable_module(base)
        self.server.enable_module(vtk_view)

        self.state.setdefault("scalarbar_probe", [])
        self.state.client_only("scalarbar_probe", "scalarbar_probe_available")

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
                        f"{{{{ {color_min}.toFixed(6) }}}}", classes="scalarbar-left"
                    )
                    html.Img(
                        src=(img_src, None),
                        style="height: 100%; width: 100%;",
                        classes="rounded-lg border-thin",
                        mousemove="scalarbar_probe = [$event.x, $event.target.getBoundingClientRect()]",
                        mouseenter="scalarbar_probe_available = 1",
                        mouseleave="scalarbar_probe_available = 0",
                        __events=["mousemove", "mouseenter", "mouseleave"],
                    )
                    html.Div(
                        v_show=("scalarbar_probe_available", False),
                        classes="scalar-cursor",
                        style=(
                            "`left: ${scalarbar_probe?.[0] - scalarbar_probe?.[1]?.left}px`",
                        ),
                    )
                    html.Div(
                        f"{{{{ {color_max}.toFixed(6) }}}}", classes="scalarbar-right"
                    )
            html.Span(
                f"{{{{ (({color_max} - {color_min}) * (scalarbar_probe?.[0] - scalarbar_probe?.[1]?.left) / scalarbar_probe?.[1]?.width + {color_min}).toFixed(6) }}}}"
            )
