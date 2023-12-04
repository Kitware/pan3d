# How to use Pan3D in a Jupyter Notebook

Running Pan3D in a Jupyter notebook will allow data scientists to incorporate the tool into their existing workflow and facilitate greater collaboration between teammates. This tutorial assumes you have a running Jupyter notebook. You can refer to the [notebook examples][notebook-examples-link] from Pan3D. You can run these examples on Binder [here][binder-link].
<!-- TODO add Binder link -->


1. In your current kernel, install Pan3D: pip install pan3d.
In the first cell of your notebook, import Pan3D’s DatasetBuilder class.
        from pan3d import DatasetBuilder

2. Instantiate a builder.

        builder = DatasetBuilder()

3. Prepare a configuration for the builder to import. This can come from a previously exported configuration file from Pan3D or it can be defined as a dictionary. Refer to `import_config_xarray.ipynb` for an example using a configuration file path or `pangeo_forge.ipynb` for an example using a configuration dictionary. Call the import function with this configuration.

        builder.import_config(config)

4. If you’d like finer control of the configuration process, you can call individual state setters on the builder by referring to the [API documentation](../api/dataset_builder.md) for the `DatasetBuilder` class. Refer to `manual_config.ipynb` for an example using these API methods.

5. After configuring the builder instance, you can show the Pan3D viewer as cell output.

        await builder.viewer.ready()
        builder.viewer

6. If you’d like to do more advanced rendering than the Pan3D viewer allows, you can still use the DatasetBuilder class for mesh preparation. You can access the mesh with `builder.mesh` and use it in a PyVista rendering pipeline. Refer to `advanced_pyvista_rendering.ipynb` for an example of this technique, which leverages PyVista plotting to generate an animated GIF of timesteps in the dataset.


[notebook-examples-link]: https://github.com/Kitware/pan3d/tree/main/examples/jupyter
[binder-link]: https://mybinder.org/v2/gh/Kitware/pan3d/main?labpath=examples%2Fjupyter
