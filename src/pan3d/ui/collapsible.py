from trame.widgets import vuetify3 as v3
from trame_client.widgets.core import AbstractElement


class CollapsableSection(AbstractElement):
    id_count = 0

    def __init__(self, title, var_name=None, expended=False):
        super().__init__(None)
        CollapsableSection.id_count += 1
        show = var_name or f"show_section_{CollapsableSection.id_count}"
        with v3.VCardSubtitle(
            classes="px-0 ml-n3 d-flex align-center font-weight-bold pointer",
            click=f"{show} = !{show}",
        ) as container:
            v3.VIcon(
                f"{{{{ {show} ? 'mdi-menu-down' : 'mdi-menu-right' }}}}",
                size="sm",
                classes="pa-0 ma-0",
            )
            container.add_child(title)
        self.content = v3.VSheet(
            border="opacity-25 thin",
            classes="overflow-hidden mx-auto mt-1 mb-2",
            rounded="lg",
            v_show=(show, expended),
        )
