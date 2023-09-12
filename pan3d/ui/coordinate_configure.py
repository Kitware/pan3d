from trame.widgets import vuetify3 as vuetify


class CoordinateConfigure(vuetify.VCard):
    def __init__(
        self,
        axes,
        coordinates,
        coordinate_info,
        coordinate_select_axis_function,
        coordinate_change_slice_function,
        axis_info=None,  # Defined only after an axis is selected for this coord
    ):
        super().__init__(width="100%", classes="ml-3 mb-1")

        with self:
            # Open expansion panel by default
            with vuetify.VExpansionPanels(
                model_value=([0],),
                accordion=True,
                v_show=coordinate_info,
            ):
                with vuetify.VExpansionPanel():
                    vuetify.VExpansionPanelTitle("{{ %s?.name }}" % coordinate_info)
                    with vuetify.VExpansionPanelText():
                        vuetify.VCardSubtitle("Select values")
                        with vuetify.VContainer(
                            classes="d-flex pa-0", style="column-gap: 3px"
                        ):
                            vuetify.VTextField(
                                model_value=("%s?.start" % coordinate_info, 0),
                                label="Start",
                                hide_details=True,
                                density="compact",
                                type="number",
                                min=("%s?.range[0]" % coordinate_info, 0),
                                max=("%s?.stop" % coordinate_info, 0),
                                __properties=[("min", "min"), ("max", "max")],
                                input=(
                                    coordinate_change_slice_function,
                                    f"[{coordinate_info}.name, 'start', $event.target.value]",
                                ),
                                __events=[("input", "input.prevent")],
                            )
                            vuetify.VTextField(
                                model_value=("%s?.stop" % coordinate_info, 0),
                                label="Stop",
                                hide_details=True,
                                density="compact",
                                type="number",
                                min=("%s?.start" % coordinate_info, 0),
                                max=("%s?.range[1]" % coordinate_info, 0),
                                __properties=[("min", "min"), ("max", "max")],
                                input=(
                                    coordinate_change_slice_function,
                                    f"[{coordinate_info}.name, 'stop', $event.target.value]",
                                ),
                                __events=[("input", "input.prevent")],
                            )
                            vuetify.VTextField(
                                model_value=("%s?.step" % coordinate_info, 0),
                                label="Step",
                                hide_details=True,
                                density="compact",
                                type="number",
                                min="1",
                                max=("%s?.range[1]" % coordinate_info, 0),
                                __properties=[("min", "min"), ("max", "max")],
                                input=(
                                    coordinate_change_slice_function,
                                    f"[{coordinate_info}.name, 'step', $event.target.value]",
                                ),
                                __events=[("input", "input.prevent")],
                            )
                        vuetify.VDivider(classes="pb-3 mt-3", thickness="3")
                        with vuetify.VSelect(
                            label="Assign axis",
                            items=(axes,),
                            item_title="label",
                            item_value="name_var",
                            model_value=(
                                axis_info["name_var"] if axis_info else "undefined",
                            ),
                            clearable=True,
                            click_clear=(
                                coordinate_select_axis_function,
                                # args: coord name, current axis, new axis
                                f"[{axis_info['name_var']}, '{axis_info['name_var']}', 'undefined']",
                            )
                            if axis_info
                            else "undefined",
                        ):
                            # use a slot for defining change function
                            # so input value is not changed in this instance of the card.
                            # if this change is not prevented, the select maintains the last input
                            # if this card becomes visible again
                            with vuetify.Template(
                                v_slot_item="{ props, item, parent }"
                            ):
                                vuetify.VListItem(
                                    v_bind="props",
                                    title="{{ props.title }}",
                                    click=(
                                        coordinate_select_axis_function,
                                        # args: coord name, current axis, new axis
                                        f"""[
                                            {coordinate_info}.name,
                                            '{axis_info["name_var"] if axis_info else "undefined"}',
                                            props.value
                                        ]""",
                                    ),
                                )
