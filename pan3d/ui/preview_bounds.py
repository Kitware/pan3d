from trame_client.widgets.core import HtmlElement


class PreviewBounds(HtmlElement):
    def __init__(self, children=None, **kwargs):
        super().__init__("preview-bounds", children, **kwargs)
        self._attr_names += [
            "preview",
            "axes",
            "coordinates",
        ]
        self._event_names += [
            ("update_bounds", "update-bounds"),
        ]
