import math
import numpy as np
from vtkmodules.vtkFiltersCore import vtkAppendFilter
from vtkmodules.vtkCommonCore import vtkPoints

from vtkmodules.numpy_interface import dataset_adapter as dsa
from vtkmodules.util import vtkConstants, numpy_support
from vtkmodules.util.vtkAlgorithm import VTKPythonAlgorithmBase


def ProcessPoint(point, radius, scale):
    theta = point[0]
    phi = 90 - point[1]
    rho = point[2] * scale + radius if not point[2] == 0 else radius
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

    def SetDataLayer(self, isData_):
        if not self.isData == isData_:
            self.isData = isData_
            self.Modified()

    def SetScalingFactor(self, scale_):
        if not self.scale == float(scale_):
            self.scale = float(scale_)
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
            pRadius = (self.radius + 10) if self.isData else self.radius
            outPoints = np.array(
                list(map(lambda x: ProcessPoint(x, pRadius, self.scale), inPoints))
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
