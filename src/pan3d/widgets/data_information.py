"""Data Information widget for displaying dataset metadata."""

from pan3d.ui.collapsible import CollapsableSection
from trame.widgets import html
from trame.widgets import vuetify3 as v3


class DataInformation(CollapsableSection):
    """
    Data information display widget that matches the original behavior.

    Extends CollapsableSection to provide a collapsible panel for dataset information.
    """

    def __init__(self, xarray_info="xarray_info"):
        """Initialize the DataInformation widget."""
        super().__init__("Data information", "show_data_information")

        self._var_name = xarray_info
        self.state.setdefault(xarray_info, [])

        with self.content:
            with v3.VTable(density="compact", hover=True):
                with html.Tbody():
                    with html.Template(v_for=f"item, i in {xarray_info}", key="i"):
                        with v3.VTooltip():
                            with html.Template(v_slot_activator="{ props }"):
                                with html.Tr(v_bind="props", classes="pointer"):
                                    with html.Td(
                                        classes="d-flex align-center text-no-wrap"
                                    ):
                                        v3.VIcon(
                                            "{{ item.icon }}",
                                            size="sm",
                                            classes="mr-2",
                                        )
                                        html.Div("{{ item.name }}")
                                    html.Td(
                                        "{{ item.length }}",
                                        classes="text-right",
                                    )

                            with v3.VTable(
                                density="compact",
                                theme="dark",
                                classes="no-bg ma-0 pa-0",
                            ):
                                with html.Tbody():
                                    with html.Tr(
                                        v_for="attr, j in item.attrs",
                                        key="j",
                                    ):
                                        html.Td(
                                            "{{ attr.key }}",
                                        )
                                        html.Td(
                                            "{{ attr.value }}",
                                        )

    def update_information(self, xr, available_arrays=None):
        xarray_info = []
        coords = set(xr.coords.keys())
        data = set(available_arrays or [])
        for name in xr.variables:
            icon = "mdi-variable"
            order = 3
            length = f"({','.join(xr[name].dims)})"
            attrs = []
            if name in coords:
                icon = "mdi-ruler"
                order = 1
                length = xr[name].size
                shape = xr[name].shape
                if length > 1 and len(shape) == 1:
                    attrs.append(
                        {
                            "key": "range",
                            "value": f"[{xr[name].values[0]}, {xr[name].values[-1]}]",
                        }
                    )
            if name in data:
                icon = "mdi-database"
                order = 2
            xarray_info.append(
                {
                    "order": order,
                    "icon": icon,
                    "name": name,
                    "length": length,
                    "type": str(xr[name].dtype),
                    "attrs": attrs
                    + [
                        {"key": "type", "value": str(xr[name].dtype)},
                    ]
                    + [
                        {"key": str(k), "value": str(v)}
                        for k, v in xr[name].attrs.items()
                    ],
                }
            )
        xarray_info.sort(key=lambda item: item["order"])

        # Update UI
        self.state[self._var_name] = xarray_info
