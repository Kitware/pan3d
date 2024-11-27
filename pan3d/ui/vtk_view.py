from trame.decorators import TrameApp, change
from trame.widgets import html, vtk as vtkw, vuetify3 as v3, vtklocal as wasm

from pan3d.utils.constants import VIEW_UPS
from pan3d.ui.css import base, vtk_view


@TrameApp()
class Pan3DView(html.Div):
    def __init__(
        self,
        render_window,
        import_pending="import_pending",
        axis_names="axis_names",
        local_rendering=None,
        widgets=None,
        **kwargs,
    ):
        super().__init__(classes="pan3d-view", **kwargs)

        # Activate CSS
        self.server.enable_module(base)
        self.server.enable_module(vtk_view)

        # Initialize conditional widgets
        vtkw.initialize(self.server)
        wasm.initialize(self.server)

        self._import_pending = import_pending
        self.render_window = render_window
        self.renderer = render_window.GetRenderers().GetFirstRenderer()
        self.camera = self.renderer.active_camera

        # Expose view_reset_clipping_range
        self.ctrl.view_reset_clipping_range = self.renderer.ResetCameraClippingRange

        # Reserved state with default
        self.state.setdefault("view_3d", True)
        self.state.setdefault(import_pending, False)

        with self:
            # 3D view
            if local_rendering is not None:
                if local_rendering == "wasm":
                    with wasm.LocalView(
                        self.render_window,
                        throttle_rate=10,
                        listeners=("wasm_listeners", {}),
                    ) as view:
                        self.ctrl.view_update_force = view.update
                        self.ctrl.view_update = view.update_throttle
                        self.ctrl.view_reset_camera = view.reset_camera
                        camera_id = view.get_wasm_id(self.camera)
                        self.state.setdefault("wasm_camera", None)
                        self.state.wasm_listeners = {
                            camera_id: {
                                "ModifiedEvent": {
                                    "wasm_camera": {
                                        "position": [camera_id, "Position"],
                                        "view_up": [camera_id, "ViewUp"],
                                        "focal_point": [camera_id, "FocalPoint"],
                                    }
                                }
                            }
                        }
                        for w in widgets or []:
                            view.register_widget(w)
                else:
                    with vtkw.VtkLocalView(self.render_window) as view:
                        self.ctrl.view_update = view.update
                        self.ctrl.view_reset_camera = view.reset_camera
                        view.set_widgets(widgets or [])
            else:
                with vtkw.VtkRemoteView(
                    self.render_window, interactive_ratio=1
                ) as view:
                    self.ctrl.view_update = view.update
                    self.ctrl.view_reset_camera = view.reset_camera

            # Scroll locking overlay
            html.Div(v_show=("view_locked", False), classes="view-lock")

            # 3D toolbox
            with v3.VCard(classes="view-toolbar pa-1", rounded="lg"):
                with v3.VTooltip(text="Lock view interaction"):
                    with html.Template(v_slot_activator="{ props }"):
                        v3.VBtn(
                            v_bind="props",
                            flat=True,
                            density="compact",
                            icon=(
                                "view_locked ? 'mdi-lock-outline' : 'mdi-lock-off-outline'",
                            ),
                            click="view_locked = !view_locked",
                        )
                v3.VDivider(classes="my-1")
                with v3.VTooltip(text="Reset camera"):
                    with html.Template(v_slot_activator="{ props }"):
                        v3.VBtn(
                            v_bind="props",
                            flat=True,
                            density="compact",
                            icon="mdi-crop-free",
                            click=self.ctrl.view_reset_camera,
                        )
                v3.VDivider(classes="my-1")
                with v3.VTooltip(text="Toggle between 3D/2D interaction"):
                    with html.Template(v_slot_activator="{ props }"):
                        v3.VBtn(
                            v_bind="props",
                            flat=True,
                            density="compact",
                            icon=("view_3d ? 'mdi-rotate-orbit' : 'mdi-cursor-move'",),
                            click="view_3d = !view_3d",
                        )
                v3.VDivider(classes="my-1")
                with v3.VTooltip(text="Rotate left 90"):
                    with html.Template(v_slot_activator="{ props }"):
                        v3.VBtn(
                            v_bind="props",
                            flat=True,
                            density="compact",
                            icon="mdi-rotate-left",
                            click=(self.rotate_camera, "[-1]"),
                        )
                with v3.VTooltip(text="Rotate right 90"):
                    with html.Template(v_slot_activator="{ props }"):
                        v3.VBtn(
                            v_bind="props",
                            flat=True,
                            density="compact",
                            icon="mdi-rotate-right",
                            click=(self.rotate_camera, "[+1]"),
                        )
                v3.VDivider(classes="my-1")
                with v3.VTooltip(
                    text=(f"`Look toward ${{ {axis_names}[0] || 'X' }}`",)
                ):
                    with html.Template(v_slot_activator="{ props }"):
                        v3.VBtn(
                            v_bind="props",
                            flat=True,
                            density="compact",
                            icon="mdi-axis-x-arrow",
                            click=(self.reset_camera_to_axis, "[[1,0,0]]"),
                        )
                with v3.VTooltip(text=(f"`Look toward ${{ {axis_names}[1] || 'Y'}}`",)):
                    with html.Template(v_slot_activator="{ props }"):
                        v3.VBtn(
                            v_bind="props",
                            flat=True,
                            density="compact",
                            icon="mdi-axis-y-arrow",
                            click=(self.reset_camera_to_axis, "[[0,1,0]]"),
                        )

                with v3.VTooltip(text=(f"`Look toward ${{ {axis_names}[2] || 'Z'}}`",)):
                    with html.Template(v_slot_activator="{ props }"):
                        v3.VBtn(
                            v_bind="props",
                            flat=True,
                            density="compact",
                            icon="mdi-axis-z-arrow",
                            click=(self.reset_camera_to_axis, "[[0,0,1]]"),
                        )
                v3.VDivider(classes="my-1")
                with v3.VTooltip(text="Look toward at an angle"):
                    with html.Template(v_slot_activator="{ props }"):
                        v3.VBtn(
                            v_bind="props",
                            flat=True,
                            density="compact",
                            icon="mdi-axis-arrow",
                            click=(self.reset_camera_to_axis, "[[1,1,1]]"),
                        )

    def reset_camera_to_axis(self, axis):
        camera = self.renderer.active_camera
        camera.focal_point = (0, 0, 0)
        camera.position = axis
        camera.view_up = VIEW_UPS.get(tuple(axis))
        self.renderer.ResetCamera()
        self.ctrl.view_update(push_camera=True)

    def rotate_camera(self, direction):
        camera = self.renderer.active_camera
        a = [*camera.view_up]
        b = [camera.focal_point[i] - camera.position[i] for i in range(3)]
        view_up = [
            direction * (a[1] * b[2] - a[2] * b[1]),
            direction * (a[2] * b[0] - a[0] * b[2]),
            direction * (a[0] * b[1] - a[1] * b[0]),
        ]
        camera.view_up = view_up

        self.ctrl.view_update(push_camera=True)

    @change("wasm_camera")
    def _on_camera(self, wasm_camera, **_):
        if wasm_camera is None:
            return

        for k, v in wasm_camera.items():
            setattr(self.camera, k, v)

    @change("view_3d")
    def _on_view_type_change(self, view_3d, **_):
        # FIXME properly swap interactor style
        if view_3d:
            # self.interactor.GetInteractorStyle().SetCurrentStyleToTrackballCamera()
            self.renderer.GetActiveCamera().SetParallelProjection(0)
        else:
            # self.interactor.GetInteractorStyle().SetCu()
            self.renderer.GetActiveCamera().SetParallelProjection(1)

        if not self.state[self._import_pending]:
            self.ctrl.view_reset_camera()


class Pan3DScalarBar(v3.VTooltip):
    def __init__(self, img_src, color_min="color_min", color_max="color_max", **kwargs):
        super().__init__(location="top")

        # Activate CSS
        self.server.enable_module(base)
        self.server.enable_module(vtk_view)

        self.state.setdefault("scalarbar_probe", [])
        self.state.client_only("scalarbar_probe", "scalarbar_probe_available")

        with self:
            # Content
            with html.Template(v_slot_activator="{ props }"):
                with html.Div(
                    classes="scalarbar",
                    rounded="pill",
                    v_bind="props",
                    **kwargs,
                ):
                    html.Div(
                        f"{{{{ {color_min}.toFixed(6) }}}}", classes="scalarbar-left"
                    )
                    html.Img(
                        src=(img_src, None),
                        style="height: 100%; width: 100%;",
                        classes="rounded-lg border-thin",
                        mousemove="scalarbar_probe = [$event.x, $event.target.getBoundingClientRect()]",
                        mouseenter="scalarbar_probe_available = 1",
                        mouseleave="scalarbar_probe_available = 0",
                        __events=["mousemove", "mouseenter", "mouseleave"],
                    )
                    html.Div(
                        v_show=("scalarbar_probe_available", False),
                        classes="scalar-cursor",
                        style=(
                            "`left: ${scalarbar_probe?.[0] - scalarbar_probe?.[1]?.left}px`",
                        ),
                    )
                    html.Div(
                        f"{{{{ {color_max}.toFixed(6) }}}}", classes="scalarbar-right"
                    )
            html.Span(
                f"{{{{ (({color_max} - {color_min}) * (scalarbar_probe?.[0] - scalarbar_probe?.[1]?.left) / scalarbar_probe?.[1]?.width + {color_min}).toFixed(6) }}}}"
            )
