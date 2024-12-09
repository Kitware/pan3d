import json
from pathlib import Path
import numpy as np

from vtkmodules.vtkRenderingCore import vtkColorTransferFunction, vtkActor
from vtkmodules.vtkCommonCore import vtkLookupTable

PRESETS = {
    item.get("Name"): item
    for item in json.loads(Path(__file__).with_name("presets.json").read_text())
}

LUTS = {}


def update_range(lut: vtkColorTransferFunction, data_range):
    prev_min, prev_max = lut.GetRange()
    prev_delta = prev_max - prev_min

    if prev_delta < 0.001:
        return

    node = [0, 0, 0, 0, 0, 0]
    next_delta = data_range[1] - data_range[0]
    next_nodes = []

    for i in range(lut.GetSize()):
        lut.GetNodeValue(i, node)
        node[0] = next_delta * (node[0] - prev_min) / prev_delta + data_range[0]
        next_nodes.append(list(node))

    lut.RemoveAllPoints()
    for n in next_nodes:
        lut.AddRGBPoint(*n)


def get_preset(preset_name: str) -> vtkColorTransferFunction:
    if preset_name in LUTS:
        return LUTS[preset_name]

    lut = LUTS.setdefault(preset_name, vtkColorTransferFunction())
    preset = PRESETS[preset_name]
    srgb = np.array(preset["RGBPoints"])
    color_space = preset["ColorSpace"]

    if color_space == "Diverging":
        lut.SetColorSpaceToDiverging()
    elif color_space == "HSV":
        lut.SetColorSpaceToHSV()
    elif color_space == "Lab":
        lut.SetColorSpaceToLab()
    elif color_space == "RGB":
        lut.SetColorSpaceToRGB()
    elif color_space == "CIELAB":
        lut.SetColorSpaceToLabCIEDE2000()

    if "NanColor" in preset:
        lut.SetNanColor(preset["NanColor"])

    # Always RGB points
    lut.RemoveAllPoints()
    for arr in np.split(srgb, len(srgb) / 4):
        lut.AddRGBPoint(arr[0], arr[1], arr[2], arr[3])

    return lut


def set_preset(lut: vtkLookupTable, preset_name: str, n_colors=255):
    colors = get_preset(preset_name)
    min, max = colors.GetRange()
    delta = max - min
    lut.SetNumberOfTableValues(n_colors)
    for i in range(n_colors):
        x = min + (delta * i / n_colors)
        rgb = colors.GetColor(x)
        lut.SetTableValue(i, *rgb)
    lut.Build()


# --------------------------------------------------------

hsv_colors = {
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
    data = json.loads(Path(__file__).with_name("presets.json").read_text())
    for cmap in data:
        name = cmap["Name"]
        srgb = np.array(cmap["RGBPoints"])
        tfunc = vtkColorTransferFunction()
        for arr in np.split(srgb, len(srgb) / 4):
            tfunc.AddRGBPoint(arr[0], arr[1], arr[2], arr[3])
        info = {"TF": tfunc, "Range": (srgb[0], srgb[-4])}
        rgb_colors[name] = info
except Exception as e:
    print("Error loading diverging color maps : ", e)


def convert_tfunc_to_lut(tfunc: vtkColorTransferFunction, tfrange):
    lut = vtkLookupTable()
    lut.SetNumberOfTableValues(256)
    tflen = tfrange[1] - tfrange[0]
    for i in range(256):
        t = tfrange[0] + tflen * i / 255
        rgb = list(tfunc.GetColor(t))
        lut.SetTableValue(i, rgb[0], rgb[1], rgb[2])
    lut.Build()
    return lut


def apply_preset(actor: vtkActor, srange, preset: str, nan_color=[0, 0, 0, 0]) -> None:
    if preset in list(hsv_colors.keys()):
        lut = vtkLookupTable()
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
        lut.SetNanColor(nan_color)
        lut.Build()
    elif preset in list(rgb_colors.keys()):
        info = rgb_colors[preset]
        tfunc = info["TF"]
        tfrange = info["Range"]
        lut = convert_tfunc_to_lut(tfunc, tfrange)
        lut.SetNanColor(nan_color)
        mapper = actor.GetMapper()
        mapper.SetLookupTable(lut)
        mapper.SetScalarRange(srange[0], srange[1])


def use_preset(sactor: vtkActor, dactor: vtkActor, sbar: vtkActor, preset: str) -> None:
    """
    Given the slice, data, and scalar bar actor, applies the provided preset
    and updates the actors and the scalar bar
    """
    srange = sactor.GetMapper().GetScalarRange()
    drange = dactor.GetMapper().GetScalarRange()
    actors = [sactor, dactor]
    ranges = [srange, drange]
    for actor, range in zip(actors, ranges):
        apply_preset(actor, range, preset)
    sactor.GetMapper().SetScalarRange(srange[0], srange[1])
    dactor.GetMapper().SetScalarRange(drange[0], drange[1])
    sbar.SetLookupTable(sactor.GetMapper().GetLookupTable())


def update_preset(actor: vtkActor, sbar: vtkActor, logcale: bool) -> None:
    """
    Given an actor, scalar bar, and the option for whether to use log scale,
    make changes to the lookup table for the actor, and update the scalar bar
    """
    lut = actor.GetMapper().GetLookupTable()
    if logcale:
        lut.SetScaleToLog10()
    else:
        lut.SetScaleToLinear()
    lut.Build()
    sbar.SetLookupTable(lut)


COLOR_PRESETS = [
    *list(hsv_colors.keys()),
    *list(rgb_colors.keys()),
]
