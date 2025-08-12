"""Basic rendering settings UI component for Pan3D explorers."""

import numpy as np

from pan3d.ui.collapsible import CollapsableSection
from pan3d.widgets.color_by import ColorBy
from trame.decorators import change
from trame.widgets import vuetify3 as v3


class RenderingSettingsBasic(CollapsableSection):
    """
    Basic rendering settings component that provides array selection
    and color mapping controls.

    This component includes:
    - Data array selection
    - Color by variable selection
    - Color preset and range controls
    """

    def __init__(self, source=None, update_rendering=None, **kwargs):
        """
        Initialize the RenderingSettingsBasic component.

        Parameters:
            source: VTK source object for data
            update_rendering: Callback function to update rendering
            **kwargs: Additional arguments passed to CollapsableSection
        """
        super().__init__("Rendering", "show_rendering", **kwargs)
        self.source = source

        with self.content:
            v3.VSelect(
                placeholder="Data arrays",
                prepend_inner_icon="mdi-database",
                hide_selected=True,
                v_model=("data_arrays", []),
                items=("data_arrays_available", []),
                multiple=True,
                hide_details=True,
                density="compact",
                chips=True,
                closable_chips=True,
                flat=True,
                variant="solo",
            )
            v3.VDivider()
            self.color_by = ColorBy(
                color_by_name="color_by",
                preset_name="color_preset",
                color_min_name="color_min",
                color_max_name="color_max",
                nan_color_name="nan_color",
                reset_color_range=self.reset_color_range,
            )

    def reset_color_range(self):
        """Reset the color range to the min and max values of the selected data array."""
        color_by = self.color_by.color_by
        ds = self.source()
        array = (
            ds.point_data[color_by]
            if color_by in ds.point_data.keys()
            else ds.cell_data[color_by]
            if color_by in ds.cell_data.keys()
            else None
        )
        if array is not None:
            self.color_by.color_min = float(np.min(array))
            self.color_by.color_max = float(np.max(array))
        else:
            self.color_by.color_min = 0.0
            self.color_by.color_max = 1.0

        self.ctrl.view_update()

    @change("data_arrays")
    def _on_array_selection(self, data_arrays, **_):
        # if self.state.import_pending:
        #    return
        self.state.dirty_data = True
        if self.source is not None:
            self.source.arrays = data_arrays

        if self.source is None or self.source.input is None:
            self.color_by.data_arrays = []
        else:
            self.color_by.set_data_arrays_from_vtk(self.source())

    def update_from_source(self, source=None):
        raise NotImplementedError(
            """
            This method needs to be implemented in the specialization of this class.
            Please override it in the necessary class representing the rendering settings for the Explorer.
            """
        )
