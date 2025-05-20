import math

import numpy as np
from vtkmodules.numpy_interface import dataset_adapter as dsa
from vtkmodules.util import numpy_support, vtkConstants
from vtkmodules.util.vtkAlgorithm import VTKPythonAlgorithmBase
from vtkmodules.vtkCommonCore import vtkPoints
from vtkmodules.vtkFiltersCore import vtkAppendFilter


def ProcessPoint(point, radius, scale):
    theta = point[0]
    phi = 90 - point[1]
    rho = point[2] * scale + radius if point[2] != 0 else radius
    x = rho * math.sin(math.radians(phi)) * math.cos(math.radians(theta))
    y = rho * math.sin(math.radians(phi)) * math.sin(math.radians(theta))
    z = rho * math.cos(math.radians(phi))
    return [x, y, z]


class ProjectToSphere(VTKPythonAlgorithmBase):
    def __init__(self):
        super().__init__(
            nInputPorts=1, nOutputPorts=1, outputType="vtkUnstructuredGrid"
        )
        self.__Dims = -1
        self.isData = False
        self.radius = 6378
        self.scale = 1.0
        self._bump_radius = 10

    def SetDataLayer(self, isData_):
        if self.isData != isData_:
            self.isData = isData_
            self.Modified()

    def SetScalingFactor(self, scale_):
        if self.scale != float(scale_):
            self.scale = float(scale_)
            self.Modified()

    @property
    def bump_radius(self):
        return self._bump_radius

    @bump_radius.setter
    def bump_radius(self, v):
        if v != self._bump_radius:
            self._bump_radius = v
            self.Modified()

    def RequestData(self, request, inInfo, outInfo):
        inData = self.GetInputData(inInfo, 0, 0)
        outData = self.GetOutputData(outInfo, 0)
        if not inData.IsA("vtkUnstructuredGrid"):
            afilter = vtkAppendFilter()
            afilter.AddInputData(inData)
            afilter.Update()
            outData.DeepCopy(afilter.GetOutput())
        else:
            outData.DeepCopy(inData)

        outWrap = dsa.WrapDataObject(outData)
        try:
            inPoints = np.array(outWrap.Points)
            pRadius = (self.radius + self._bump_radius) if self.isData else self.radius
            outPoints = np.array(
                [ProcessPoint(x, pRadius, self.scale) for x in inPoints]
            )
        except Exception as e:
            print(e)
        _coords = numpy_support.numpy_to_vtk(
            outPoints, deep=True, array_type=vtkConstants.VTK_FLOAT
        )
        vtk_coords = vtkPoints()
        vtk_coords.SetData(_coords)
        outWrap.SetPoints(vtk_coords)

        return 1
