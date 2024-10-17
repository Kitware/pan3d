from trame.widgets import vuetify3 as v3


class NumericField(v3.VTextField):
    def __init__(self, update_event, **kwargs):
        super().__init__(
            **kwargs,
            on_blur=(update_event, "[Number($event.target.value)]"),
            on_enter=(update_event, "[Number($event.target.value)]"),
            __events=[("on_blur", "blur"), ("on_enter", "keyup.enter")],
        )
