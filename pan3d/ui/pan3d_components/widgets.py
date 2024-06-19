from trame_client.widgets.core import AbstractElement
from . import module

__all__ = [
    "PreviewBounds",
]


class HtmlElement(AbstractElement):
    def __init__(self, _elem_name, children=None, **kwargs):
        super().__init__(_elem_name, children, **kwargs)
        if self.server:
            self.server.enable_module(module)


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
