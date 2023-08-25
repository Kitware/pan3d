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
                        with vuetify.VSelect(
                            label="Assign axis",
                            items=(axes,),
                            item_text="label",
                            item_value="name_var",
                            value=name_var or "undefined",
                            clearable=True,
                            click_clear=(
                                coordinate_select_axis,
                                # args: coord name, current axis, new axis
                                f"[{name_var}, '{name_var}', 'undefined']",
                            ),
                        ):
                            # use a slot for defining change function
                            # so input value is not changed in this instance of the card.
                            # if this change is not prevented, the select maintains the last input
                            # if this card becomes visible again
                            with vuetify.Template(
                                v_slot_item="{ attrs, item, parent }"
                            ):
                                with vuetify.VListItem(
                                    v_bind="attrs",
                                    click=(
                                        coordinate_select_axis,
                                        # args: coord name, current axis, new axis
                                        f"""[
                                            {name_var or name or "undefined"},
                                            '{name_var or "undefined"}',
                                            item.name_var
                                        ]""",
                                        # make selection dropdown disappear
                                        "parent.$el.style.display = 'none'",
                                    ),
                                ):
                                    with vuetify.VListItemContent():
                                        vuetify.VListItemTitle("{{ item.label }}")
