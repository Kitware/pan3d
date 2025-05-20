import numpy as np
import xarray as xr

from pan3d.xarray.datasets import imagedata_to_rectilinear
from pan3d.xarray.io import dataset_to_xarray
from pan3d.xarray.io import read as vtk_read


def test_engine_is_available():
    assert "vtk" in xr.backends.list_engines()


def test_read_vtr(vtr_path):
    ds = xr.open_dataset(vtr_path, engine="vtk")
    truth = vtk_read(vtr_path)
    assert np.allclose(ds["air"].values.ravel(), truth.point_data["air"].ravel())
    assert np.allclose(ds["x"].values, truth.x_coordinates)
    assert np.allclose(ds["y"].values, truth.y_coordinates)
    assert np.allclose(ds["z"].values, truth.z_coordinates)
    accessor_ds = ds["air"].vtk.dataset(x="x", y="y", z="z")
    assert accessor_ds == truth


def test_read_vti(vti_path):
    ds = xr.open_dataset(vti_path, engine="vtk")
    truth = vtk_read(vti_path)
    truth_r = imagedata_to_rectilinear(truth)
    assert np.allclose(ds["RTData"].values.ravel(), truth.point_data["RTData"].ravel())
    assert np.allclose(ds["x"].values, truth_r.x_coordinates)
    assert np.allclose(ds["y"].values, truth_r.y_coordinates)
    assert np.allclose(ds["z"].values, truth_r.z_coordinates)

    assert ds["RTData"].vtk.dataset(x="x", y="y", z="z") == truth_r


def test_read_vts(vts_path):
    ds = xr.open_dataset(vts_path, engine="vtk")
    truth = vtk_read(vts_path)
    assert np.allclose(
        ds["Elevation"].values.ravel(), truth.point_data["Elevation"].ravel()
    )
    assert np.allclose(ds["x"].values, truth.x_coordinates)
    assert np.allclose(ds["y"].values, truth.y_coordinates)
    assert np.allclose(ds["z"].values, truth.z_coordinates)
    # accessor_ds = ds["Elevation"].vtk.dataset(x="x", y="y", z="z")
    # assert accessor_ds == truth


def test_convert_vtr(vtr_path):
    truth = vtk_read(vtr_path)
    ds = dataset_to_xarray(truth)
    mesh = ds["air"].vtk.dataset(x="x", y="y", z="z")
    assert np.array_equal(ds["air"].values.ravel(), truth.point_data["air"].ravel())
    assert np.may_share_memory(
        ds["air"].values.ravel(), truth.point_data["air"].ravel()
    )
    assert np.array_equal(mesh.x_coordinates, truth.x_coordinates)
    assert np.array_equal(mesh.y_coordinates, truth.y_coordinates)
    assert np.array_equal(mesh.z_coordinates, truth.z_coordinates)
    assert np.may_share_memory(mesh.z_coordinates, truth.z_coordinates)
    assert mesh == truth


def test_convert_vti(vti_path):
    truth = vtk_read(vti_path)
    ds = dataset_to_xarray(truth)
    truth_r = imagedata_to_rectilinear(truth)
    mesh = ds["RTData"].vtk.dataset(x="x", y="y", z="z")
    assert np.array_equal(
        ds["RTData"].values.ravel(), truth.point_data["RTData"].ravel()
    )
    assert np.may_share_memory(
        ds["RTData"].values.ravel(), truth.point_data["RTData"].ravel()
    )
    assert np.array_equal(mesh.x_coordinates, truth_r.x_coordinates)
    assert np.array_equal(mesh.y_coordinates, truth_r.y_coordinates)
    assert np.array_equal(mesh.z_coordinates, truth_r.z_coordinates)
    assert mesh == truth_r


def test_convert_vts(vts_path):
    print("=" * 10, "test_convert_vts", "=" * 10)
    truth = vtk_read(vts_path)
    ds = dataset_to_xarray(truth)
    assert np.array_equal(
        ds["Elevation"].values.ravel(), truth.point_data["Elevation"].ravel()
    )
    assert np.may_share_memory(
        ds["Elevation"].values.ravel(), truth.point_data["Elevation"].ravel()
    )
    mesh = ds["Elevation"].vtk.dataset(x="x", y="y", z="z")
    assert mesh == truth
