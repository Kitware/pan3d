import math
from xarray.tutorial import open_dataset
from vtkmodules.vtkCommonCore import vtkPoints, vtkMath
from vtkmodules.vtkCommonDataModel import vtkStructuredGrid
from vtkmodules.vtkIOLegacy import vtkDataSetWriter

from ..coords.parametric_vertical import get_formula


class Formula_ocean_s_coordinate_g2:
    def __init__(self, xr_dataset, s, c, eta, depth, depth_c):
        self.xr_dataset = xr_dataset
        self.s = self.xr_dataset[s].values
        self.c = self.xr_dataset[c].values
        self.eta = self.xr_dataset[eta].values
        self.depth = self.xr_dataset[depth].values
        self.depth_c = self.xr_dataset[depth_c].values

    def __call__(self, n, k, j, i):
        return self.eta[n, j, i] + (self.eta[n, j, i] + self.depth[j, i]) * (
            self.depth_c * self.s[k] + self.depth[j, i] * self.c[k]
        ) / (self.depth_c + self.depth[j, i])


def main():
    ds = open_dataset("ROMS_example")

    t = 0
    salt = ds.salt  # (ocean_time, s_rho, eta_rho, xi_rho)
    lon_rho = ds.lon_rho.values  # (eta_rho, xi_rho)
    lat_rho = ds.lat_rho.values  # (eta_rho, xi_rho)

    # 1D coords
    eta_rho = ds.eta_rho
    xi_rho = ds.xi_rho
    s_rho = (
        ds.s_rho
    )  # (s_rho) | ocean_s_coordinate_g2 | formula_terms= "s: s_rho C: Cs_r eta: zeta depth: h depth_c: hc"

    formula = get_formula(ds, "s_rho")

    # ocean_s_coordinate_g2
    # z(n,k,j,i) = eta(n,j,i) + (eta(n,j,i) + depth(j,i)) * S(k,j,i)
    # S(k,j,i) = (depth_c * s(k) + depth(j,i) * C(k)) / (depth_c + depth(j,i))
    # formula_terms = "s: var1 C: var2 eta: var3 depth: var4 depth_c: var5"
    # - s: s_rho
    # - C: Cs_r
    # - eta: zeta
    # - depth: h
    # - depth_c: hc

    earth_radius = 6378137  # in meters
    bias = earth_radius
    scale = 100

    n_points = s_rho.size * eta_rho.size * xi_rho.size
    points = vtkPoints()
    points.SetDataTypeToDouble()
    points.Allocate(n_points)

    for k in range(s_rho.size):
        for j in range(eta_rho.size):
            for i in range(xi_rho.size):
                lon = vtkMath.RadiansFromDegrees(lon_rho[j, i])
                lat = vtkMath.RadiansFromDegrees(lat_rho[j, i])
                h = bias + scale * formula(t, k, j, i)
                points.InsertNextPoint(
                    h * math.cos(lon) * math.cos(lat),
                    h * math.sin(lon) * math.cos(lat),
                    h * math.sin(lat),
                )

    mesh = vtkStructuredGrid()
    mesh.SetExtent(0, xi_rho.size - 1, 0, eta_rho.size - 1, 0, s_rho.size - 1)
    mesh.points = points
    mesh.point_data["salt"] = salt[t].values.ravel()

    writer = vtkDataSetWriter()
    writer.SetInputData(mesh)
    writer.SetFileName("rom_salt.vtk")
    writer.Write()


if __name__ == "__main__":
    main()
