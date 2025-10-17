def setup(renderer):
    try:
        from vtkmodules import vtkRenderingAnari
    except ImportError:
        return

    anariPass = vtkRenderingAnari.vtkAnariPass()
    renderer.SetPass(anariPass)

    anariDevice = anariPass.GetAnariDevice()
    anariDevice.SetupAnariDeviceFromLibrary("environment", "default", False)

    anariRenderer = anariPass.GetAnariRenderer()
    anariRenderer.SetSubtype("raycast")
    anariRenderer.SetParameterf("ambientRadiance", 0.8)

    # VisRTX specific settings
    # anariRenderer.SetParameterf("lightFalloff", 0.5)
    anariRenderer.SetParameterb("denoise", True)
    anariRenderer.SetParameteri("pixelSamples", 10)
    # anariRenderer.SetParameteri("ambientSamples", 5)
