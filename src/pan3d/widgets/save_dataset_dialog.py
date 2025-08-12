"""Save Dataset Dialog widget for consistent save functionality across explorers."""

from trame.widgets import vuetify3 as v3


class SaveDatasetDialog(v3.VDialog):
    """
    A reusable dialog for saving datasets.

    Used across all explorers to provide consistent save functionality.
    """

    def __init__(
        self,
        save_callback=None,
        v_model=("show_save_dialog", False),
        save_path_model=("save_path", "output.nc"),
        title="Save Dataset",
        width=500,
        **kwargs,
    ):
        """
        Initialize the SaveDatasetDialog widget.

        Args:
            save_callback: Function to call when save is confirmed
            v_model: State binding for dialog visibility
            save_path_model: State binding for save path
            title: Dialog title
            width: Dialog width
            **kwargs: Additional VDialog properties
        """
        super().__init__(v_model=v_model, width=width, **kwargs)

        with self:
            with v3.VCard():
                v3.VCardTitle(title)
                with v3.VCardText():
                    v3.VTextField(
                        v_model=save_path_model,
                        label="File Path",
                        hint="Specify the path where the dataset will be saved",
                        persistent_hint=True,
                        prepend_inner_icon="mdi-file",
                        variant="outlined",
                        density="compact",
                    )
                with v3.VCardActions():
                    v3.VSpacer()
                    v3.VBtn(
                        "Cancel",
                        click=f"{v_model[0]} = false",
                        text=True,
                    )
                    v3.VBtn(
                        "Save",
                        click=(self.save_callback, f"[{save_path_model[0]}]"),
                        variant="elevated",
                        color="primary",
                    )

    @property
    def save_callback(self):
        """Get the save callback function."""
        return self._save_callback

    @save_callback.setter
    def save_callback(self, value):
        """Set the save callback function."""
        self._save_callback = value
