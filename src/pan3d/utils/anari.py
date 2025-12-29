def setup(renderer):
    try:
        from vtkmodules import vtkRenderingAnari
    except ImportError:
        return

    anariPass = vtkRenderingAnari.vtkAnariPass()
    renderer.SetPass(anariPass)
    # Call render on the render window to initialize ANARI
    renderer.GetRenderWindow().Render()
    # Configure ANARI renderer parameters
    anariRenderer = anariPass.GetAnariRenderer()
    anariRenderer.SetParameterf("ambientRadiance", 1.0)

    # VisRTX specific settings
    anariRenderer.SetParameterb("denoise", True)
    anariRenderer.SetParameteri("pixelSamples", 5)
    anariRenderer.SetParameteri("ambientSamples", 1)

    return anariPass
