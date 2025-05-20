import json
from pathlib import Path

import numpy as np
from vtkmodules.vtkCommonCore import vtkLookupTable
from vtkmodules.vtkRenderingCore import vtkColorTransferFunction

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
