import pan3d.xarray.accessor  # noqa
from vtkmodules import register_vtk_module_dependencies


register_vtk_module_dependencies("vtkCommonDataModel", "pan3d.xarray.vtk_data_model")
