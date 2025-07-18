"""Shared UI components for Pan3D explorers to reduce code duplication."""

from pan3d.utils.constants import XYZ
from trame.widgets import html
from trame.widgets import vuetify3 as v3


class TimeSlider:
    """Shared time slider component used across multiple explorers."""

    def __init__(
        self,
        slice_t="slice_t",
        slice_t_max="slice_t_max",
        t_labels="t_labels",
        max_time_width="max_time_width",
        max_time_index_width="max_time_index_width",
    ):
        self.slice_t = slice_t
        self.slice_t_max = slice_t_max
        self.t_labels = t_labels
        self.max_time_width = max_time_width
        self.max_time_index_width = max_time_index_width

    def create(self):
        """Create and return the time slider component."""
        with v3.VTooltip(text="Time") as tooltip:
            with html.Template(v_slot_activator="{ props }"):
                with html.Div(
                    v_bind="props",
                    classes="d-flex flex-row align-center px-2",
                ):
                    v3.VIcon("mdi-clock-outline", classes="mr-2")
                    html.Pre(
                        f"{{{{ {self.t_labels}[{self.slice_t}] }}}}",
                        classes="mr-2",
                        style=(f"`min-width: ${{{self.max_time_width}}}rem;`",),
                    )
                    v3.VSlider(
                        v_model=(self.slice_t, 0),
                        min=0,
                        max=(self.slice_t_max, 0),
                        step=1,
                        hide_details=True,
                        density="compact",
                        flat=True,
                        variant="solo",
                        classes="mx-2",
                    )
                    html.Div(
                        f"{{{{ {self.slice_t} + 1 }}}}/{{{{ {self.slice_t_max} + 1 }}}}",
                        classes="mx-2 text-right",
                        style=(f"`min-width: ${{{self.max_time_index_width}}}rem;`",),
                    )
        return tooltip


class ScalingControls:
    """Shared scaling controls for X, Y, Z axes in row/column format."""

    def __init__(
        self,
        axis_names="axis_names",
        scale_x="scale_x",
        scale_y="scale_y",
        scale_z="scale_z",
    ):
        self.axis_names = axis_names
        self.scale_x = scale_x
        self.scale_y = scale_y
        self.scale_z = scale_z

    def create(self):
        """Create and return the scaling controls component."""
        with v3.VTooltip(text="Representation scaling") as tooltip:
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
                    for i, (_, scale_var) in enumerate(
                        [
                            ("x", self.scale_x),
                            ("y", self.scale_y),
                            ("z", self.scale_z),
                        ]
                    ):
                        with v3.VCol(classes="pa-0", v_if=f"{self.axis_names}?.[{i}]"):
                            v3.VTextField(
                                v_model=(scale_var, 1),
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
        return tooltip


class UpdateButton:
    """Shared update button for 3D view."""

    def __init__(
        self,
        update_rendering,
        data_arrays="data_arrays",
        dirty_data="dirty_data",
    ):
        self.update_rendering = update_rendering
        self.data_arrays = data_arrays
        self.dirty_data = dirty_data

    def create(self):
        """Create and return the update button component."""
        return v3.VBtn(
            "Update 3D view",
            block=True,
            classes="text-none",
            flat=True,
            density="compact",
            rounded=0,
            disabled=(f"!{self.data_arrays}.length",),
            color=(f"{self.dirty_data} ? 'orange-darken-2': 'primary'",),
            click=(self.update_rendering, "[true]"),
        )


class AxisSlicingControl:
    """Shared axis slicing control for a single axis."""

    def __init__(
        self,
        axis,
        axis_index,
        axis_names="axis_names",
        slice_extents="slice_extents",
        dataset_bounds="dataset_bounds",
    ):
        self.axis = axis
        self.axis_index = axis_index
        self.axis_names = axis_names
        self.slice_extents = slice_extents
        self.dataset_bounds = dataset_bounds
        self.axis_lower = axis.lower()

    def create(self):
        """Create and return the axis slicing control component."""
        axis_name = f"{self.axis_names}[{self.axis_index}]"
        slice_type = f"slice_{self.axis_lower}_type"
        slice_range = f"slice_{self.axis_lower}_range"
        slice_cut = f"slice_{self.axis_lower}_cut"
        slice_step = f"slice_{self.axis_lower}_step"
        bounds_start = self.axis_index * 2
        bounds_end = bounds_start + 1

        # Different tooltip text formats for preview vs globe styles
        with v3.VTooltip(
            v_if=f"{self.axis_names}?.[{self.axis_index}]",
            text=(
                f"`${{{axis_name}}}: [${{{self.dataset_bounds}[{bounds_start}]}}, "
                f"${{{self.dataset_bounds}[{bounds_end}]}}] "
                f"${{{slice_type} ==='range' ? ('(' + {slice_range}.map((v,i) => v+1).concat({slice_step}).join(', ') + ')'): {slice_cut}}}`",
            ),
        ) as tooltip:
            with html.Template(v_slot_activator="{ props }"):
                with html.Div(
                    classes="d-flex",
                    v_if=f"{self.axis_names}?.[{self.axis_index}]",
                    v_bind="props",
                ):
                    v3.VRangeSlider(
                        v_if=f"{slice_type} === 'range'",
                        prepend_icon=f"mdi-axis-{self.axis_lower}-arrow",
                        v_model=(slice_range, None),
                        min=(f"{self.slice_extents}[{axis_name}][0]",),
                        max=(f"{self.slice_extents}[{axis_name}][1]",),
                        step=1,
                        hide_details=True,
                        density="compact",
                        flat=True,
                        variant="solo",
                    )
                    v3.VSlider(
                        v_else=True,
                        prepend_icon=f"mdi-axis-{self.axis_lower}-arrow",
                        v_model=(slice_cut, 0),
                        min=(f"{self.slice_extents}[{axis_name}][0]",),
                        max=(f"{self.slice_extents}[{axis_name}][1]",),
                        step=1,
                        hide_details=True,
                        density="compact",
                        flat=True,
                        variant="solo",
                    )
                    v3.VCheckbox(
                        v_model=(slice_type, "range"),
                        true_value="range",
                        false_value="cut",
                        true_icon="mdi-crop",
                        false_icon="mdi-box-cutter",
                        hide_details=True,
                        density="compact",
                        size="sm",
                        classes="mx-2",
                    )
        return tooltip


class AxisSlicingControls:
    """Container for all three axis slicing controls."""

    def __init__(
        self,
        axis_names="axis_names",
        slice_extents="slice_extents",
        dataset_bounds="dataset_bounds",
    ):
        self.controls = [
            AxisSlicingControl(axis, i, axis_names, slice_extents, dataset_bounds)
            for i, axis in enumerate(XYZ)
        ]

    def create(self):
        """Create and return all axis slicing controls."""
        components = []
        for i, control in enumerate(self.controls):
            components.append(control.create())
            if i < len(self.controls) - 1:
                components.append(v3.VDivider())
        return components


class SliceSteppingControls:
    """Shared slice stepping controls for Level of Details."""

    def __init__(self, axis_names="axis_names"):
        self.axis_names = axis_names

    def create(self):
        """Create and return the slice stepping controls."""
        with v3.VTooltip(text="Level Of Details / Slice stepping") as tooltip:
            with html.Template(v_slot_activator="{ props }"):
                with v3.VRow(
                    v_bind="props",
                    no_gutter=True,
                    classes="align-center my-0 mx-0 border-b-thin",
                ):
                    v3.VIcon(
                        "mdi-stairs",
                        classes="ml-2 text-medium-emphasis",
                    )
                    for i, axis in enumerate(XYZ):
                        with v3.VCol(classes="pa-0", v_if=f"{self.axis_names}?.[{i}]"):
                            v3.VTextField(
                                v_model_number=(f"slice_{axis.lower()}_step", 1),
                                hide_details=True,
                                density="compact",
                                flat=True,
                                variant="solo",
                                reverse=True,
                                raw_attrs=['min="1"'],
                                type="number",
                            )
        return tooltip
