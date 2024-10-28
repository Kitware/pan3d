r"""
Module that extend VTK data_model until available mainstream
"""

from vtkmodules.util.data_model import PointSet
from vtkmodules.vtkCommonDataModel import (
    vtkStructuredGrid,
)


@vtkStructuredGrid.override
class vtkStructuredGrid(PointSet, vtkStructuredGrid):
    @property
    def dimensions(self):
        # handle deprecation
        dims = [0, 0, 0]
        self.GetDimensions(dims)
        return dims

    @property
    def x_coordinates(self):
        return self.points[:, 0].reshape(self.dimensions, order="F")

    @property
    def y_coordinates(self):
        return self.points[:, 1].reshape(self.dimensions, order="F")

    @property
    def z_coordinates(self):
        return self.points[:, 2].reshape(self.dimensions, order="F")
