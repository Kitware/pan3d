import json
import vtk
import zarr
import logging
from . import module

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class ZarrHierarchy:
    def __init__(self):
        self.node_hierarchy = { "/": {"id": "/", "children": []} }

    def create_node(self, name, obj):
        # print(name, obj)
        new_node = { "id": name, "name": name.split("/")[-1], "children": [] }

        if isinstance(obj, zarr.core.Array):
            new_node["dimensions"] = obj.shape
            new_node["type"] = f"{obj.dtype}"

        parent_id = "/".join(name.split("/")[:-1])
        if len(parent_id) == 0:
            parent_id = "/"
        if parent_id in self.node_hierarchy:
            self.node_hierarchy[parent_id]["children"].append(new_node)
        self.node_hierarchy[name] = new_node

    @property
    def root(self):
        return self.node_hierarchy["/"]

    @property
    def children(self):
        return self.root["children"]


# ---------------------------------------------------------
# Zarr helper
# ---------------------------------------------------------

class Viewer:
    def __init__(self, server, zarr_store=None, zarr_path=None):
        state, ctrl = server.state, server.controller
        server.enable_module(module)

        # VTK
        self._vtk_grid = vtk.vtkImageData()
        self._vtk_renderer = vtk.vtkRenderer()
        self._vtk_render_window = vtk.vtkRenderWindow()
        self._vtk_render_window.AddRenderer(self._vtk_renderer)
        self._vtk_render_window_interactor = vtk.vtkRenderWindowInteractor()
        self._vtk_render_window_interactor.SetRenderWindow(self._vtk_render_window)
        self._vtk_render_window_interactor.GetInteractorStyle().SetCurrentStyleToTrackballCamera()
        self._vtk_mapper = vtk.vtkDataSetMapper()
        self._vtk_actor = vtk.vtkActor()
        self._vtk_mapper.SetInputData(self._vtk_grid)
        self._vtk_actor.SetMapper(self._vtk_mapper)
        self._vtk_renderer.AddActor(self._vtk_actor)
        self._vtk_renderer.ResetCamera()

        # to fix
        self._vtk_grid.SetDimensions(10, 10, 10)
        self._vtk_actor.GetProperty().SetEdgeVisibility(1)

        # Zarr
        self._zarr = zarr_store
        if zarr_path is not None:
            self._zarr = zarr.open(zarr_path, mode="r")

        self.hierarchy = ZarrHierarchy()
        self._zarr.visititems(self.hierarchy.create_node)

        # state
        state.zarr_tree = self.hierarchy.children

        # controller
        ctrl.get_render_window = self.get_render_window


    def get_render_window(self):
        return self._vtk_render_window



# ---------------------------------------------------------
# Server binding
# ---------------------------------------------------------


def initialize(server, zarr=None):
    state, ctrl = server.state, server.controller
    add_on = dict(zarr_store=None, zarr_path=None)
    if isinstance(zarr, str):
        add_on["zarr_path"] = zarr
    else:
        add_on["zarr_store"] = zarr

    viewer = Viewer(server, **add_on)
    return viewer
