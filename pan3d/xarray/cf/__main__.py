import sys
from xarray.tutorial import open_dataset
from .utils import XArrayDataSetCFHelper
from pathlib import Path
import xarray as xr
from vtkmodules.vtkIOLegacy import vtkDataSetWriter

from pan3d.catalogs.xarray import ALL_ENTRIES
from .coords.meta import MetaArrayMapping


def main():
    output_name = "test.vtk"
    if Path(sys.argv[-1]).exists():
        input_file = Path(sys.argv[-1]).resolve()
        output_name = f"{input_file.name}.vtk"
        ds = xr.open_dataset(str(input_file))
    else:
        output_name = f"{sys.argv[-1]}.vtk"
        ds = open_dataset(sys.argv[-1])

    helper = XArrayDataSetCFHelper(ds)
    print("Arrays:", helper.available_arrays)

    helper.array_selection = [helper.available_arrays[0]]

    print("=" * 60)
    print("Coordinates:")
    print("=" * 60)
    for name in ds.coords:
        print(helper.get_info(name))
    print("=" * 60)
    print("Data:")
    print("=" * 60)
    for name in ds.data_vars:
        print(helper.get_info(name))
    print("=" * 60)

    if helper.x_info:
        print(f"{'-'*60}\nX\n{'-'*60}", helper.x_info)
    if helper.y_info:
        print(f"{'-'*60}\nY\n{'-'*60}", helper.y_info)
    if helper.z_info:
        print(f"{'-'*60}\nZ\n{'-'*60}", helper.z_info)
    if helper.t_info:
        print(f"{'-'*60}\nT\n{'-'*60}", helper.t_info)

    mesh = helper.mesh
    print(mesh)

    writer = vtkDataSetWriter()
    writer.SetInputData(mesh)
    writer.SetFileName(output_name)
    writer.Write()


# -----------------------------------------------------------------------------
def main2():
    DATASETS = [item.get("name") for item in ALL_ENTRIES]
    FILES = ["/Users/sebastien.jourdain/Downloads/sampleGenGrid3.nc"]
    for ds_name in DATASETS:
        ds = open_dataset(ds_name)
        meta = MetaArrayMapping(ds)

        print("-" * 60)
        print(ds_name)
        print("-" * 60)
        print(meta)

    for f_path in FILES:
        input_file = Path(f_path).resolve()
        ds = xr.open_dataset(str(input_file))
        meta = MetaArrayMapping(ds)

        print("-" * 60)
        print(input_file.name)
        print("-" * 60)
        print(meta)


# -----------------------------------------------------------------------------
def save_dataset(ds_name, field):
    ds = open_dataset(ds_name)
    meta = MetaArrayMapping(ds)

    print(meta)

    print("-" * 60)
    print("spherical=ON")
    salt_spherical = meta.get_mesh(fields=[field], spherical=True)

    print("-" * 60)
    print("spherical=OFF")
    salt_euclidian = meta.get_mesh(fields=[field], spherical=False)
    print("-" * 60)

    writer = vtkDataSetWriter()

    if salt_spherical:
        writer.SetInputData(salt_spherical)
        writer.SetFileName(f"{ds_name}-{field}-spherical.vtk")
        writer.Write()

    if salt_euclidian:
        writer.SetInputData(salt_euclidian)
        writer.SetFileName(f"{ds_name}-{field}-euclidian.vtk")
        writer.Write()


def main3():
    write = [
        # ("ROMS_example","salt"), # ok
        # ("ROMS_example","zeta"), # ok
        # ("air_temperature", "air"), # ok
        # ("air_temperature_gradient", "Tair"), # ok
        # ("basin_mask", "basin"), # ok
        # ("rasm", "Tair"), # not following convention
        ("eraint_uvz", "v"),
        # ("ersstv5", "sst"), # bounds
    ]

    for ds, field in write:
        print("#" * 80)
        print(ds)
        print("#" * 80)
        save_dataset(ds, field)


if __name__ == "__main__":
    main3()
