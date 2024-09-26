import json
import vtk
import os
import numpy as np

hsv_colors = {
    "Rainbow": {
        "Hue": (0.666, 0.0),
        "Saturation": (1.0, 1.0),
        "Range": (1.0, 1.0),
    },
    "Inv Rainbow": {
        "Hue": (0.0, 0.666),
        "Saturation": (1.0, 1.0),
        "Range": (1.0, 1.0),
    },
    "Greyscale": {
        "Hue": (0.0, 0.0),
        "Saturation": (0.0, 0.0),
        "Range": (0.0, 1.0),
    },
    "Inv Greyscale": {
        "Hue": (0.0, 0.666),
        "Saturation": (0.0, 0.0),
        "Range": (1.0, 0.0),
    },
}

rgb_colors = {}
try:
    with open(os.path.dirname(__file__) + os.sep + "Presets.json", "r") as file:
        data = json.load(file)
        for cmap in data:
            name = cmap["Name"]
            srgb = np.array(cmap["RGBPoints"])
            tfunc = vtk.vtkColorTransferFunction()
            for arr in np.split(srgb, len(srgb) / 4):
                tfunc.AddRGBPoint(arr[0], arr[1], arr[2], arr[3])
            info = {"TF": tfunc, "Range": (srgb[0], srgb[-4])}
            rgb_colors[name] = info
except Exception as e:
    print("Error loading diverging color maps : ", e)


def convert_tfunc_to_lut(tfunc: vtk.vtkColorTransferFunction, tfrange):
    lut = vtk.vtkLookupTable()
    lut.SetNumberOfTableValues(256)
    tflen = tfrange[1] - tfrange[0]
    for i in range(256):
        t = tfrange[0] + tflen * i / 255
        rgb = list(tfunc.GetColor(t))
        lut.SetTableValue(i, rgb[0], rgb[1], rgb[2])
    lut.Build()
    return lut


def apply_preset(actor: vtk.vtkActor, srange, preset: str) -> None:
    if preset in list(hsv_colors.keys()):
        lut = vtk.vtkLookupTable()
        lut.SetNumberOfTableValues(256)
        mapper = actor.GetMapper()
        mapper.SetLookupTable(lut)
        preset = hsv_colors[preset]
        hue = preset["Hue"]
        sat = preset["Saturation"]
        rng = preset["Range"]
        lut.SetHueRange(hue[0], hue[1])
        lut.SetSaturationRange(sat[0], sat[1])
        lut.SetValueRange(rng[0], rng[1])
        lut.Build()
    elif preset in list(rgb_colors.keys()):
        info = rgb_colors[preset]
        tfunc = info["TF"]
        tfrange = info["Range"]
        lut = convert_tfunc_to_lut(tfunc, tfrange)
        mapper = actor.GetMapper()
        mapper.SetLookupTable(lut)
        mapper.SetScalarRange(srange[0], srange[1])
