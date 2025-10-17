import json
import traceback
from pathlib import Path

from pan3d import catalogs as pan3d_catalogs
from pan3d.utils.constants import SLICE_VARS, XYZ
from pan3d.utils.convert import update_camera
from pan3d.xarray.algorithm import vtkXArrayRectilinearSource
from trame.app import TrameApp, asynchronous
from trame.decorators import change


class Explorer(TrameApp):
    def __init__(
        self, xarray=None, source=None, pipeline=None, server=None, local_rendering=None
    ):
        """
        Parameters:
            xarray : An instance of a xarray dataset
            source : vtkXArrayRectilinearSource or another VTKAlgorithm wrapper over the xarray dataset
            pipeline: List of instantiated VTK filters to be appended to the explorer's pipeline
                      The filters must be limited to single source, and variables available on the xarray data
            server (str/server): Trame server name or instance.
            local_rendering (str): If provided (wasm, vtkjs) local rendering will be used

        CLI options:
            - `--import-state`: Pass a string with this argument to specify a startup configuration.
                              This value must be a local path to a JSON file which adheres to the
                              schema specified in the [Configuration Files documentation](../api/configuration.md).
                              A dataset specified in this configuration will override any value passed to `--xarray-*`
            - `--xarray-file`: Provide path to xarray file
            - `--xarray-url`: Provide URL to xarray dataset
            - `--wasm`: Use WASM for local rendering
            - `--vtkjs`: Use vtk.js for local rendering
            - `--anari`: Use anari for remote rendering
        """
        super().__init__(server, client_type="vue3")

        parser = self.server.cli
        explorer = parser.add_argument_group("Explorer Properties")
        explorer.add_argument(
            "--import-state",
            help="Pass a string with this argument to specify a startup configuration. This value must be a local path to a JSON file which adheres to the schema specified in the [Configuration Files documentation](../api/configuration.md). A dataset specified in this configuration will override any value passed to `--xarray-*`",
        )
        explorer.add_argument(
            "--xarray-file",
            help="Provide path to xarray file",
        )
        explorer.add_argument(
            "--xarray-url",
            help="Provide URL to xarray dataset",
        )

        rendering = parser.add_argument_group("Rendering Properties")
        # Local rendering setup
        rendering.add_argument(
            "--wasm",
            help="Use WASM for local rendering",
            action="store_true",
        )
        rendering.add_argument(
            "--vtkjs",
            help="Use vtk.js for local rendering",
            action="store_true",
        )
        rendering.add_argument(
            "--anari",
            help="Use anari for remote rendering",
            action="store_true",
        )

        # CLI
        args, _ = self.server.cli.parse_known_args()
        # Local rendering
        self.local_rendering = local_rendering
        self.anari = args.anari
        if args.wasm:
            self.local_rendering = "wasm"
        if args.vtkjs:
            self.local_rendering = "vtkjs"

        self.state.nan_colors = [
            [0, 0, 0, 1],
            [0.99, 0.99, 0.99, 1],
            [0.6, 0.6, 0.6, 1],
            [1, 0, 0, 1],
            [0, 1, 0, 1],
            [0, 0, 1, 1],
            [0.9, 0.9, 0.9, 0],
        ]
        self.state.nan_color = 2

        # Initialize load button state
        self.state.can_load = True
        self.state.load_button_text = "Load"

        self.ui = None

        # Initialize source
        self.xarray = None
        self.source = None

        if source is not None:
            self.source = source
            self.xarray = source.input
        elif xarray is not None:
            self.source = vtkXArrayRectilinearSource(input=xarray)
            self.xarray = xarray

        # Process CLI
        self.ctrl.on_server_ready.add(self._process_cli)

    # -------------------------------------------------------------------------
    # Trame API
    # -------------------------------------------------------------------------

    def _process_cli(self, **_):
        args, _ = self.server.cli.parse_known_args()

        # import state
        if args.import_state:
            self._import_file_from_path(args.import_state)

        # load xarray (file)
        elif args.xarray_file:
            self.state.import_pending = True
            with self.state:
                self.load_dataset("file", args.xarray_file)
                self.state.data_origin_id = str(Path(args.xarray_file).resolve())
            self.state.import_pending = False

        # load xarray (url)
        elif args.xarray_url:
            self.state.import_pending = True
            with self.state:
                self.load_dataset("url", args.xarray_url)
                self.state.data_origin_id = args.xarray_url
            self.state.import_pending = False

        # Load given XArray
        elif self.xarray is not None:
            self.state.show_data_information = True
            self.ctrl.xr_update_info(self.source.input, self.source.available_arrays)
            self.ctx.rendering.update_from_source(self.source)
        # Initialize xarray tutorial datasets if no dataset is provided
        elif self.state.data_origin_source == "xarray":
            results, *_ = pan3d_catalogs.search("xarray")
            self.state.data_origin_ids = [v["name"] for v in results]
            self.state.data_origin_id_to_desc = {
                v["name"]: v["description"] for v in results
            }

    def start(self, **kwargs):
        """Initialize the UI and start the server for XArray Viewer."""
        self.ui.server.start(**kwargs)

    @property
    async def ready(self):
        """Start and wait for the XArray Viewer corroutine to be ready."""
        await self.ui.ready

    @change("data_origin_order")
    def _on_order_change(self, **_):
        if self.state.import_pending:
            return

        self.state.load_button_text = "Load"
        self.state.can_load = True

    @change("data_origin_source")
    def _on_data_origin_source(self, data_origin_source, **kwargs):
        if self.state.import_pending:
            return

        self.state.data_origin_id = ""
        results, *_ = pan3d_catalogs.search(data_origin_source)
        self.state.data_origin_ids = [v["name"] for v in results]
        self.state.data_origin_id_to_desc = {
            v["name"]: v["description"] for v in results
        }

    @change("data_origin_id")
    def _on_data_origin_id(self, data_origin_id, data_origin_source, **kwargs):
        if self.state.import_pending:
            return

        self.state.load_button_text = "Load"
        self.state.can_load = True

        if data_origin_source == "file":
            self.state.data_origin_id_error = not Path(data_origin_id).exists()
        elif self.state.data_origin_id_error:
            self.state.data_origin_id_error = False

    # -----------------------------------------------------
    # UI Components
    # -----------------------------------------------------
    @change("color_by", "color_preset", "color_min", "color_max", "nan_color")
    def _on_color_properties_change(self, **_):
        if getattr(self, "_updating_color", False):
            return  # Prevent recursion

        if self.mapper:
            self._updating_color = True
            try:
                self.ctx.rendering.color_by.configure_mapper(self.mapper)
                self.ctx.scalar_bar.preset = self.state.color_preset
                self.ctx.scalar_bar.set_color_range(
                    self.state.color_min, self.state.color_max
                )
                self.ctrl.view_update()
            finally:
                self._updating_color = False

    @change("slice_t", *[var.format(axis) for axis in XYZ for var in SLICE_VARS])
    def on_change(self, slice_t, **_):
        source = self.source
        if source is None:
            return

        if self.state.import_pending:
            return

        slices = {source.t: slice_t}
        for axis in XYZ:
            axis_name = getattr(source, axis)
            if axis_name is None:
                continue

            if self.state[f"slice_{axis}_type"] == "range":
                if self.state[f"slice_{axis}_range"] is None:
                    continue
                slices[axis_name] = [
                    *self.state[f"slice_{axis}_range"],
                    int(self.state[f"slice_{axis}_step"]),
                ]
                slices[axis_name][1] += 1  # end is exclusive
            else:
                slices[axis_name] = self.state[f"slice_{axis}_cut"]

        source.slices = slices
        ds = source()
        self.state.dataset_bounds = ds.bounds

        self.ctrl.view_reset_clipping_range()
        self.ctrl.view_update()

    @change("slice_t")
    def _on_slice_t(self, slice_t, **_):
        if self.state.import_pending:
            return

        self.source.t_index = slice_t
        self.ctrl.view_update()

    def extend_pipeline(self, head=None, pipeline=None):
        """
        Appends a sequence of VTK filters to the explorer's visualization pipeline.

        This method connects the given `pipeline` of VTK filters starting from the
        specified `head` algorithm. If `pipeline` is not provided or empty, the method
        returns `head` unchanged. If `head` is None, the default starting point is `self.source`.

        Parameters
        ----------
        head : vtkAlgorithm, optional
            The VTK algorithm to use as the starting point of the pipeline.
            Defaults to `self.source` if not provided.

        pipeline : list of vtkAlgorithm, optional
            A list of instantiated VTK filters to be connected sequentially.
            For example:
                [
                    vtk.vtkPolyDataNormals(compute_cell_normals=True),
                    vtk.vtkCellCenters(),
                    vtk.vtkThreshold(lower=3.0, upper=15.0)
                ]

            All filters must expose `SetInputConnection` and `GetOutputPort`.

        Returns
        -------
        vtkAlgorithm
            The last filter in the extended pipeline (i.e., the tail).
        """
        if head is None:
            head = self.source
        tail = head
        if pipeline and len(pipeline) > 0:
            for filter in pipeline:
                filter.input_connection = tail.output_port
                tail = filter
        return tail

    # -----------------------------------------------------
    # Triggers
    # -----------------------------------------------------

    def import_file_upload(self, files):
        self.import_state(json.loads(files[0].get("content")))

    def _import_file_from_path(self, file_path):
        if file_path is None:
            return

        file_path = Path(file_path)
        if file_path.exists():
            self.import_state(json.loads(file_path.read_text("utf-8")))

    def load_dataset(self, source, id, order="C", config=None):
        self.state.data_origin_source = source
        self.state.data_origin_id = id
        self.state.load_button_text = "Loaded"
        self.state.can_load = False
        self.state.show_data_information = True

        if config is None:
            config = {
                "arrays": [],
                "slices": {},
            }

        try:
            self.source.load(
                {
                    "data_origin": {
                        "source": source,
                        "id": id,
                        "order": order,
                    },
                    "dataset_config": config,
                }
            )

            # Extract UI
            self.ctrl.xr_update_info(self.source.input, self.source.available_arrays)
            self.ctx.rendering.update_from_source(self.source)

            # no error
            self.state.data_origin_error = False
        except Exception as e:
            self.state.data_origin_error = (
                f"Error occurred while trying to load data. {e}"
            )
            self.state.data_origin_id_error = True
            self.state.load_button_text = "Load"
            self.state.can_load = True
            self.state.show_data_information = False

            print(traceback.format_exc())

    def update_rendering(self, reset_camera=False):
        raise NotImplementedError(
            """
            This method is supposed to be implemented by the Explorer.
            Please override this in the necessary Explorer class if you see this message
            """
        )

    # -----------------------------------------------------
    # Public API
    # -----------------------------------------------------

    def export_state(self, **kwargs):
        """Return a json dump of the reader and viewer state"""
        camera = self.renderer.active_camera
        state_to_export = {
            **self.source.state,
            "rendering": {
                "view_3d": self.state.view_3d,
                "color_by": self.state.color_by,
                "color_preset": self.state.color_preset,
                "color_min": self.state.color_min,
                "color_max": self.state.color_max,
                "scale_x": self.state.scale_x,
                "scale_y": self.state.scale_y,
                "scale_z": self.state.scale_z,
            },
            "camera": {
                "position": camera.position,
                "view_up": camera.view_up,
                "focal_point": camera.focal_point,
                "parallel_projection": camera.parallel_projection,
                "parallel_scale": camera.parallel_scale,
            },
            **kwargs,
        }
        return json.dumps(state_to_export, indent=2)

    def import_state(self, data_state):
        """
        Read the current state to load the data and visualization setup if any.

        Parameters:
            - data_state (dict): reader (+viewer) state to reset to
        """
        self.state.import_pending = True
        try:
            data_origin = data_state.get("data_origin")
            source = data_origin.get("source")
            id = data_origin.get("id")
            order = data_origin.get("order", "C")
            config = data_state.get("dataset_config")
            rendering_state = data_state.get("rendering", {})
            camera_state = data_state.get("camera", {})

            # load data and initial rendering setup
            with self.state:
                self.load_dataset(source, id, order, config)
                self.state.update(rendering_state)

            # override computed color range using state values
            with self.state:
                self.state.update(rendering_state)

            # update camera and render
            update_camera(self.renderer.active_camera, camera_state)
            self.update_rendering()
        finally:
            self.state.import_pending = False

    async def _save_dataset(self, file_path):
        output_path = Path(file_path).resolve()
        self.source.input.to_netcdf(output_path)

    def save_dataset(self, file_path):
        """
        Write XArray data into a file using a background task.
        So when used programmatically, make sure you await the returned task.

        Parameters:
            - file_path (str): path to use for writing the file

        Returns:
            writing task
        """
        self.state.show_save_dialog = False
        return asynchronous.create_task(self._save_dataset(file_path))
