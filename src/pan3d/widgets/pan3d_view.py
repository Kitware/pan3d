"""Pan3D View widget for VTK-based 3D visualization."""

from vtkmodules.vtkRenderingAnnotation import vtkAxesActor
from vtkmodules.vtkRenderingCore import (
    vtkRenderer,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
)

from pan3d.ui.css import base, vtk_view
from trame.widgets import html
from trame.widgets import vtk as vtk_widgets
from trame.widgets import vuetify3 as v3


class Pan3DView(html.Div):
    """
    Self-contained VTK visualization widget with interaction controls.

    Provides:
    - VTK render window with local/remote rendering options
    - Standard 3D interaction toolbar
    - Camera controls and view presets
    - Orientation marker widget

    Usage:
        view = Pan3DView(
            local_rendering="wasm",
            on_camera_change=handle_camera_update
        )
        view.add_actor(my_vtk_actor)
        view.reset_camera()
    """

    _next_id = 0

    def __init__(
        self,
        # Rendering options
        local_rendering=None,
        interactive_ratio=1,
        interactive_quality=50,
        # State variable names (optional)
        view_mode_name=None,
        lock_view_name=None,
        orientation_widget_name=None,
        # Callbacks
        on_camera_change=None,
        on_view_mode_change=None,
        # UI options
        show_toolbar=True,
        toolbar_position="bottom",
        background_color=(0.1, 0.1, 0.1),
        # VTK widgets to overlay
        widgets=None,
        **kwargs,
    ):
        """
        Create a Pan3D visualization widget.

        Parameters
        ----------
        local_rendering : str, optional
            "wasm" or "vtkjs" for client-side rendering
        interactive_ratio : int
            Image downsampling ratio during interaction
        interactive_quality : int
            JPEG quality during interaction (0-100)
        view_mode_name : str, optional
            State variable name for 2D/3D mode
        lock_view_name : str, optional
            State variable name for view lock
        orientation_widget_name : str, optional
            State variable name for orientation widget visibility
        on_camera_change : callable, optional
            Callback when camera changes
        on_view_mode_change : callable, optional
            Callback when 2D/3D mode changes
        show_toolbar : bool
            Whether to show the interaction toolbar
        toolbar_position : str
            Toolbar position: "top", "bottom", "left", "right"
        background_color : tuple
            RGB background color (0-1 range)
        widgets : list, optional
            List of VTK widgets to add to the view
        """
        super().__init__(**kwargs)

        # Activate CSS
        self.server.enable_module(base)
        self.server.enable_module(vtk_view)

        # Generate unique namespace
        Pan3DView._next_id += 1
        self._id = Pan3DView._next_id
        ns = f"pan3d_view_{self._id}"

        # Store configuration
        self.local_rendering = local_rendering
        self.interactive_ratio = interactive_ratio
        self.interactive_quality = interactive_quality
        self.show_toolbar = show_toolbar
        self.toolbar_position = toolbar_position
        self._on_camera_change = on_camera_change
        self._on_view_mode_change = on_view_mode_change

        # Initialize state variables
        self.__view_mode = view_mode_name or f"{ns}_view_mode"
        self.__lock_view = lock_view_name or f"{ns}_lock_view"
        self.__orientation_widget = (
            orientation_widget_name or f"{ns}_orientation_widget"
        )
        self.__camera_position = f"{ns}_camera_position"
        self.__camera_focal_point = f"{ns}_camera_focal_point"
        self.__camera_view_up = f"{ns}_camera_view_up"

        # Set default state
        self.state[self.__view_mode] = "3D"
        self.state[self.__lock_view] = False
        self.state[self.__orientation_widget] = True

        # Initialize VTK objects
        self._renderer = vtkRenderer()
        self._renderer.SetBackground(*background_color)

        self._render_window = vtkRenderWindow()
        self._render_window.AddRenderer(self._renderer)
        self._render_window.OffScreenRenderingOn()

        self._interactor = vtkRenderWindowInteractor()
        self._interactor.SetRenderWindow(self._render_window)
        self._interactor.GetInteractorStyle().SetCurrentStyleToTrackballCamera()

        # Set up orientation widget
        self._setup_orientation_widget()

        # Add any provided widgets
        self._widgets = widgets or []
        for widget in self._widgets:
            if hasattr(widget, "SetInteractor"):
                widget.SetInteractor(self._interactor)
            if hasattr(widget, "EnabledOn"):
                widget.EnabledOn()

        # Register state callbacks
        self.state.change(self.__view_mode)(self._on_view_mode_change)

        # Build UI directly in __init__
        with self:
            with html.Div(classes="d-flex flex-column fill-height"):
                # Toolbar positioning logic
                toolbar_orientation = (
                    "vertical"
                    if self.toolbar_position in ["left", "right"]
                    else "horizontal"
                )

                # Top toolbar
                if self.show_toolbar and self.toolbar_position == "top":
                    self._toolbar = self._create_toolbar_ui(toolbar_orientation)

                # Main view area
                with html.Div(classes="flex-grow-1 d-flex"):
                    # Left toolbar
                    if self.show_toolbar and self.toolbar_position == "left":
                        self._toolbar = self._create_toolbar_ui(toolbar_orientation)

                    # VTK render window
                    if self.local_rendering == "wasm":
                        # WebAssembly rendering
                        self._vtk_view = vtk_widgets.VtkLocalView(
                            render_window=self._render_window, classes="flex-grow-1"
                        )
                    elif self.local_rendering == "vtkjs":
                        # VTK.js rendering
                        self._vtk_view = vtk_widgets.VtkLocalView(
                            render_window=self._render_window,
                            mode="local",
                            classes="flex-grow-1",
                        )
                    else:
                        # Remote rendering
                        self._vtk_view = vtk_widgets.VtkRemoteView(
                            render_window=self._render_window,
                            interactive_ratio=self.interactive_ratio,
                            interactive_quality=self.interactive_quality,
                            interactor_events=(
                                "['LeftButtonPress', 'LeftButtonRelease', 'MouseMove', "
                                "'RightButtonPress', 'RightButtonRelease', 'MouseWheelForward', "
                                "'MouseWheelBackward', 'KeyPress']",
                            ),
                            classes="flex-grow-1",
                            StartInteraction=self._start_interaction,
                            EndInteraction=self._end_interaction,
                            MouseMove=(
                                self._on_mouse_move,
                                "[utils.vtk.event($event)]",
                            ),
                        )

                    # Right toolbar
                    if self.show_toolbar and self.toolbar_position == "right":
                        self._toolbar = self._create_toolbar_ui(toolbar_orientation)

                # Bottom toolbar
                if self.show_toolbar and self.toolbar_position == "bottom":
                    self._toolbar = self._create_toolbar_ui(toolbar_orientation)

    # -------------------------------------------------------------------------
    # Properties
    # -------------------------------------------------------------------------

    @property
    def renderer(self):
        """Get the VTK renderer."""
        return self._renderer

    @property
    def render_window(self):
        """Get the VTK render window."""
        return self._render_window

    @property
    def interactor(self):
        """Get the VTK interactor."""
        return self._interactor

    @property
    def camera(self):
        """Get the active camera."""
        return self._renderer.GetActiveCamera()

    @property
    def view_mode(self):
        """Get/set the view mode (2D/3D)."""
        return self.state[self.__view_mode]

    @view_mode.setter
    def view_mode(self, value):
        with self.state:
            self.state[self.__view_mode] = value

    @property
    def lock_view(self):
        """Get/set the view lock state."""
        return self.state[self.__lock_view]

    @lock_view.setter
    def lock_view(self, value):
        with self.state:
            self.state[self.__lock_view] = bool(value)

    # -------------------------------------------------------------------------
    # UI Building
    # -------------------------------------------------------------------------

    def _create_toolbar_ui(self, orientation):
        """Create the interaction toolbar UI."""
        with html.Div(classes=f"pa-1 d-flex align-center {orientation}") as toolbar:
            # Lock/unlock view
            v3.VBtn(
                icon=True,
                size="small",
                click=(f"{self.__lock_view} = !{self.__lock_view}",),
            ).add_child(
                v3.VIcon(
                    f"{{{self.__lock_view} ? 'mdi-lock' : 'mdi-lock-open'}}",
                    size="small",
                )
            )

            v3.VDivider(vertical=(orientation == "horizontal"))

            # 2D/3D mode
            v3.VBtnToggle(
                v_model=(self.__view_mode,),
                density="compact",
                divided=True,
                mandatory=True,
            ).add_children(
                [
                    v3.VBtn(value="2D", size="small").add_child("2D"),
                    v3.VBtn(value="3D", size="small").add_child("3D"),
                ]
            )

            v3.VDivider(vertical=(orientation == "horizontal"))

            # Camera presets
            v3.VBtn(icon="mdi-home", size="small", click=self.reset_camera)

            v3.VBtn(icon="mdi-rotate-left", size="small", click=self._rotate_left_90)

            v3.VBtn(icon="mdi-rotate-right", size="small", click=self._rotate_right_90)

            v3.VDivider(vertical=(orientation == "horizontal"))

            # Axis alignment
            for axis, icon in [
                ("X", "mdi-alpha-x"),
                ("Y", "mdi-alpha-y"),
                ("Z", "mdi-alpha-z"),
            ]:
                v3.VBtn(
                    icon=icon, size="small", click=(self._align_to_axis, f"['{axis}']")
                )

            v3.VDivider(vertical=(orientation == "horizontal"))

            # Orientation widget toggle
            v3.VBtn(
                icon="mdi-axis-arrow",
                size="small",
                color=(f"{self.__orientation_widget} ? 'primary' : ''",),
                click=(f"{self.__orientation_widget} = !{self.__orientation_widget}",),
            )

        return toolbar

    def _setup_orientation_widget(self):
        """Set up the orientation marker widget."""
        axes = vtkAxesActor()
        self._orientation_widget = vtk_widgets.vtkOrientationMarkerWidget()
        self._orientation_widget.SetOrientationMarker(axes)
        self._orientation_widget.SetInteractor(self._interactor)
        self._orientation_widget.SetViewport(0.85, 0, 1, 0.15)
        self._orientation_widget.EnabledOn()
        self._orientation_widget.InteractiveOff()

        # Bind visibility to state
        self.state.change(self.__orientation_widget)(self._toggle_orientation_widget)

    # -------------------------------------------------------------------------
    # VTK Operations
    # -------------------------------------------------------------------------

    def add_actor(self, actor):
        """Add an actor to the renderer."""
        self._renderer.AddActor(actor)

    def remove_actor(self, actor):
        """Remove an actor from the renderer."""
        self._renderer.RemoveActor(actor)

    def clear_actors(self):
        """Remove all actors from the renderer."""
        self._renderer.RemoveAllViewProps()

    def reset_camera(self):
        """Reset camera to fit all visible objects."""
        self._renderer.ResetCamera()
        self.update()

    def update(self):
        """Trigger a render update."""
        self._render_window.Render()
        if hasattr(self._vtk_view, "update"):
            self._vtk_view.update()
        self._update_camera_state()

    def set_background(self, r, g, b):
        """Set the background color."""
        self._renderer.SetBackground(r, g, b)
        self.update()

    # -------------------------------------------------------------------------
    # Event Handlers
    # -------------------------------------------------------------------------

    def _on_view_mode_change(self, mode, **kwargs):
        """Handle 2D/3D mode change."""
        if mode == "2D":
            self._interactor.GetInteractorStyle().SetCurrentStyleToImage()
        else:
            self._interactor.GetInteractorStyle().SetCurrentStyleToTrackballCamera()

        if self._on_view_mode_change:
            self._on_view_mode_change(mode)

        self.update()

    def _toggle_orientation_widget(self, visible, **kwargs):
        """Toggle orientation widget visibility."""
        if visible:
            self._orientation_widget.EnabledOn()
        else:
            self._orientation_widget.EnabledOff()
        self.update()

    def _start_interaction(self):
        """Handle start of interaction."""

    def _end_interaction(self):
        """Handle end of interaction."""
        self._update_camera_state()
        if self._on_camera_change:
            self._on_camera_change(self.camera)

    def _on_mouse_move(self, event):
        """Handle mouse move events."""

    def _update_camera_state(self):
        """Update camera state variables."""
        camera = self.camera
        with self.state:
            self.state[self.__camera_position] = list(camera.GetPosition())
            self.state[self.__camera_focal_point] = list(camera.GetFocalPoint())
            self.state[self.__camera_view_up] = list(camera.GetViewUp())

    def _rotate_left_90(self):
        """Rotate view 90 degrees left."""
        self.camera.Roll(-90)
        self.update()

    def _rotate_right_90(self):
        """Rotate view 90 degrees right."""
        self.camera.Roll(90)
        self.update()

    def _align_to_axis(self, axis):
        """Align camera to look along specified axis."""
        self._renderer.ResetCamera()
        camera = self.camera
        focal = camera.GetFocalPoint()
        distance = camera.GetDistance()

        if axis == "X":
            camera.SetPosition(focal[0] + distance, focal[1], focal[2])
            camera.SetViewUp(0, 0, 1)
        elif axis == "Y":
            camera.SetPosition(focal[0], focal[1] + distance, focal[2])
            camera.SetViewUp(0, 0, 1)
        elif axis == "Z":
            camera.SetPosition(focal[0], focal[1], focal[2] + distance)
            camera.SetViewUp(0, 1, 0)

        self.update()
