from trame.widgets import html, vuetify3 as vuetify


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
        super().__init__(width="95%", classes="ml-3 mb-1")

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
                        vuetify.VCardSubtitle("Attributes")
                        with vuetify.VTable(density="compact", v_show=coordinate_info):
                            with html.Tbody():
                                with html.Tr(
                                    v_for=f"data_attr in {coordinate_info}?.attrs",
                                ):
                                    html.Td("{{ data_attr.key }}")
                                    html.Td("{{ data_attr.value }}")

                        if axis_info and axis_info["index_var"] != "undefined":
                            vuetify.VCardSubtitle("Select index", classes="mt-3")
                            with vuetify.VSlider(
                                v_model=axis_info["index_var"],
                                min=0,
                                max=(
                                    "%s?.size - 1" % coordinate_info,
                                    0,
                                ),
                                step=1,
                                classes="mx-5",
                            ):
                                with vuetify.Template(
                                    v_slot_append="{ props, item, parent }"
                                ):
                                    vuetify.VTextField(
                                        v_model=axis_info["index_var"],
                                        min=0,
                                        max=(
                                            "%s?.size - 1" % coordinate_info,
                                            0,
                                        ),
                                        hide_details=True,
                                        density="compact",
                                        style="width: 80px",
                                        type="number",
                                        __properties=[("min", "min"), ("max", "max")],
                                    )
                        else:
                            vuetify.VCardSubtitle("Select values", classes="mt-3")
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
                                    max=("%s?.size" % coordinate_info, 0),
                                    __properties=[("min", "min"), ("max", "max")],
                                    input=(
                                        coordinate_change_slice_function,
                                        f"[{coordinate_info}.name, 'step', $event.target.value]",
                                    ),
                                    __events=[("input", "input.prevent")],
                                )

                        vuetify.VCardSubtitle("Assign axis", classes="mt-3")
                        with vuetify.VSelect(
                            items=(axes,),
                            item_title="label",
                            item_value="name_var",
                            model_value=(axis_info or "undefined",),
                            clearable=True,
                            click_clear=(
                                coordinate_select_axis_function,
                                # args: coord name, current axis, new axis
                                f"[{axis_info['name_var']}, '{axis_info['name_var']}', 'undefined']",
                            )
                            if axis_info
                            else "undefined",
                            update_modelValue=(
                                coordinate_select_axis_function,
                                # args: coord name, current axis, new axis
                                f"""[
                                    {coordinate_info}.name,
                                    '{axis_info["name_var"] if axis_info else "undefined"}',
                                    $event
                                ]""",
                            ),
                        ):
                            with vuetify.Template(
                                v_slot_selection="{ props, item, parent }"
                            ):
                                html.Span(axis_info["label"] if axis_info else "")
