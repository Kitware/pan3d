from trame.widgets import vuetify


class AxisConfigure(vuetify.VCard):
    def __init__(
        self,
        axes,
        coordinate_select_axis,
        name=None,
        name_var=None,
        index=None,
        index_var=None,
        slider_max=None,
        max_var=None,
    ):
        super().__init__(
            v_show="true" if name else (name_var,),
            width="100%",
            classes="ml-3 mb-1",
        )

        with self:
            # Open expansion panel by default
            with vuetify.VExpansionPanels(value=([0],), accordion=True):
                with vuetify.VExpansionPanel():
                    vuetify.VExpansionPanelHeader("{{ %s }}" % (name_var or name,))
                    with vuetify.VExpansionPanelContent():
                        vuetify.VSelect(
                            label="Assign axis",
                            items=(axes,),
                            item_text="label",
                            item_value="name_var",
                            clearable=True,
                            value=name_var or "undefined",
                            change=(
                                coordinate_select_axis,
                                # args: coord name, current axis, new axis
                                "[%s, '%s', $event]"
                                % (
                                    name_var or name or "undefined",
                                    name_var or "undefined",
                                ),
                            ),
                        )
