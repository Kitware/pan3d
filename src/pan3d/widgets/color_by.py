from typing import Optional

import numpy as np
from vtkmodules.vtkCommonCore import vtkLookupTable

from pan3d.utils.convert import to_image
from pan3d.utils.presets import PRESETS, set_preset
from trame.widgets import html
from trame.widgets import vuetify3 as v3

POINT_DATA = "point_data"
CELL_DATA = "cell_data"
FIELD_DATA = "field_data"


class ColorBy(html.Div):
    """
    Color settings for the XArray Explorers.
    """

    _next_id = 0

    @classmethod
    def next_id(cls):
        """Get the next unique ID for the scalar bar."""
        cls._next_id += 1
        return f"pan3d_scalarbar{cls._next_id}"

    def __init__(
        self,
        data_arrays: Optional[list[dict]] = None,
        color_by=None,
        preset="Fast",
        color_min=0.0,
        color_max=1.0,
        nan_color=0,
        color_by_name=None,
        preset_name=None,
        color_min_name=None,
        color_max_name=None,
        nan_color_name=None,
        reset_color_range=None,
        **kwargs,
    ):
        """
        Initialize the ColorBy UI component.

        Parameters
        ----------
        data_arrays : List[Dict], optional
            A list of dictionaries representing available arrays to color by.
            Each dictionary should contain keys such for name, association, and array min and max.
            The association can be 'point_data', 'cell_data', or 'field_data'
            e.g. [{'name' : 'temperature', 'assoc' : 'point_data', 'min' : 0.0, 'max' : 100.0}]

        color_by : str or None, optional
            The name of the currently selected array to color by.

        preset : str, optional
            Name of the colormap preset to use. Defaults to "Fast".

        color_min : float, optional
            Minimum value of the color mapping range. Defaults to 0.0.

        color_max : float, optional
            Maximum value of the color mapping range. Defaults to 1.0.

        nan_color : int or tuple, optional
            Color to use for NaN values (index into colormap). Defaults to 0.

        color_by_name : str or None, optional
            Name of the UI variable to bind the `color_by` selection to.

        preset_name : str or None, optional
            Name of the UI variable to bind the `preset` selection to.

        color_min_name : str or None, optional
            Name of the UI variable to bind the `color_min` value to.

        color_max_name : str or None, optional
            Name of the UI variable to bind the `color_max` value to.

        nan_color_name : str or None, optional
            Name of the UI variable to bind the `nan_color` value to.

        reset_color_range : callable or None, optional
            Optional callback function to reset the color range to the array's min/max.

        **kwargs : dict
            Additional keyword arguments passed to the parent `html.Div` component.
        """

        self._lut = vtkLookupTable()
        super().__init__(**kwargs)

        ns = self.next_id()
        # Variables that serve and input/output (interactive) can be user specified
        self.__color_by = color_by_name or f"{ns}_color_by"
        self.__color_preset = preset_name or f"{ns}_preset"
        self.__color_min = color_min_name or f"{ns}_color_min"
        self.__color_max = color_max_name or f"{ns}_color_max"
        self.__nan_color = nan_color_name or f"{ns}_nan_color"

        # Variables that are only input or only output do not need user specification
        self.__data_arrays = f"{ns}_data_arrays"
        self.__preset_image = f"{ns}_preset_img"
        self.__color_presets = f"{ns}_color_presets"

        # Register changes based on state update within the widget
        self.state.change(self.__color_preset)(self.set_preset)
        self.state.change(self.__color_by)(self.set_color_by)
        self.state.change(self.__nan_color)(self.set_nan_color)

        self.__array_infos = None
        self.data_arrays = data_arrays
        self.color_by = color_by
        self.preset = preset
        self.color_min = color_min
        self.color_max = color_max
        self.nan_color = nan_color

        with self:
            v3.VSelect(
                placeholder="Color By",
                prepend_inner_icon="mdi-format-color-fill",
                v_model=(self.__color_by, None),
                items=(self.__data_arrays, []),
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
                        v_model_number=(self.__color_min, 0.45),
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
                        v_model_number=(self.__color_max, 5.45),
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
                        click=reset_color_range,
                    )
            # v3.VDivider()
            with html.Div(classes="mx-2"):
                html.Img(
                    src=(self.__preset_image, None),
                    style="height: 0.75rem; width: 100%;",
                    classes="rounded-lg border-thin",
                )
            v3.VSelect(
                placeholder="Color Preset",
                prepend_inner_icon="mdi-palette",
                v_model=(self.__color_preset, "Fast"),
                items=(self.__color_presets, list(PRESETS.keys())),
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
                        v_model=self.__nan_color,
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

    @property
    def data_arrays(self):
        """
        Returns the arrays available to color the data by based on the list of dictionaries representing array metadata
        Each dictionary contains keys such for name, association, and array min and max.
        The association can be either of 'point_data', 'cell_data', or 'field_data'
        e.g. [{'name' : 'temperature', 'assoc' : 'point_data', 'min' : 0.0, 'max' : 100.0}]
        """
        return self.__array_infos

    @data_arrays.setter
    def data_arrays(self, array_info: list[dict]):
        """
        Controls the arrays available to color the data by based on the list of dictionaries representing array metadata
        Each dictionary should contain keys such for name, association, and array min and max.
        The association can be either of 'point_data', 'cell_data', or 'field_data'
        e.g. [{'name' : 'temperature', 'assoc' : 'point_data', 'min' : 0.0, 'max' : 100.0}]
        """
        if array_info is None:
            return
        self.__array_infos = array_info
        data_arrays = [info["name"] for info in array_info]
        self.state[self.__data_arrays] = data_arrays

        color_by = self.color_by
        # If the data arrays are empty, set color_by to None
        if array_info is None or len(data_arrays) == 0:
            self.color_by = None
        # If the color_by is not in the new data arrays, reset it to the first available
        elif color_by is None or color_by not in data_arrays:
            self.color_by = data_arrays[0]

    @property
    def color_by(self):
        return self.state[self.__color_by]

    def set_color_by(self, **kwargs):
        self.color_by = self.state[self.__color_by]

    @color_by.setter
    def color_by(self, value):
        """Set the array to color by."""
        with self.state:
            self.state[self.__color_by] = value
            if self.__array_infos:
                info = next(
                    (info for info in self.__array_infos if info["name"] == value), None
                )
                if info is not None:
                    self.color_min = float(info.get("min", self.color_min))
                    self.color_max = float(info.get("max", self.color_max))
                else:
                    self.color_min = 0.0
                    self.color_max = 1.0

    @property
    def color_by_name(self):
        return self.__color_by

    def set_preset(self, **_):
        """Set the color preset for the scalar bar."""
        self.preset = self.state[self.__color_preset]

    @property
    def preset(self):
        return self._preset

    @preset.setter
    def preset(self, value):
        """Set the color preset to color the data by."""
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

    def set_color_range(self, color_min, color_max):
        """Set the color range for the scalar bar."""
        self.state[self.__color_min] = color_min
        self.state[self.__color_max] = color_max

    @property
    def color_min(self):
        return self.state[self.__color_min]

    @color_min.setter
    def color_min(self, value):
        """Set the minimum value of the color mapping range."""
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
        """Set the maximum value of the color mapping range."""
        with self.state:
            self.state[self.__color_max] = value

    @property
    def color_max_name(self):
        return self.__color_max

    @property
    def nan_color(self):
        nan_colors = self.state.nan_colors
        nan_color = self.state[self.__nan_color]
        return nan_colors.get(nan_color, [0, 0, 0, 0])

    @nan_color.setter
    def nan_color(self, value: int):
        """Set the color for NaN values."""
        with self.state:
            self.state[self.__nan_color] = value
            nan_color = self.state.nan_colors[value]
            self._lut.SetNanColor(nan_color)

    def set_nan_color(self, **_):
        nan_colors = self.state.nan_colors
        nan_color = nan_colors[self.state[self.__nan_color]]
        self._lut.SetNanColor(nan_color)

    def set_data_arrays_from_vtk(self, dataset, associations=None):
        """Inspect dataset to extract arrays metadata. Only works with scalar fields."""
        if dataset is None:
            self.data_arrays = []
            return

        array_info = []
        if associations is None:
            associations = [POINT_DATA, CELL_DATA, FIELD_DATA]

        for association in associations:
            arrays = getattr(dataset, association, None)
            if arrays is not None:
                for inst in arrays:
                    if isinstance(inst, str):  # VTK 9.5 returns array names
                        array_name = inst
                        array = arrays[array_name]
                    else:
                        array = inst  # VTK 9.4 returns array instances
                        array_name = array.GetName()
                    # Now array is guaranteed to be the actual array object
                    array_info.append(
                        {
                            "name": array_name,
                            "min": np.min(array),
                            "max": np.max(array),
                            "assoc": association,
                        }
                    )
        self.data_arrays = array_info

    def configure_mapper(self, mapper):
        """Configure the color mapper with the current settings for any data association."""
        # Find the association type for the selected array
        assoc = None
        if self.__array_infos:
            info = next(
                (info for info in self.__array_infos if info["name"] == self.color_by),
                None,
            )
            if info is not None:
                assoc = info.get("assoc", POINT_DATA).lower()
            else:
                mapper.SetScalarVisibility(0)
                return

        # Set the color array and scalar mode based on association
        if assoc == POINT_DATA:
            mapper.SetScalarModeToUsePointFieldData()
        elif assoc == CELL_DATA:
            mapper.SetScalarModeToUseCellFieldData()
        elif assoc == FIELD_DATA:
            mapper.SetScalarModeToUseFieldData()

        set_preset(self._lut, self.preset)
        mapper.SetLookupTable(self._lut)
        mapper.SelectColorArray(self.color_by)
        mapper.SetScalarRange(self.color_min, self.color_max)
        mapper.SetScalarVisibility(1)
