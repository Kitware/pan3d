from pan3d import DatasetBuilder
from pan3d import DatasetViewer


def push_builder_state(builder):
    builder.dataset_info = {"source": "xarray", "id": "eraint_uvz"}
    builder.z = "level"
    builder.t = "month"
    builder.t_index = 1
    builder.slicing = {"longitude": [0, 90, 1], "latitude": [0, 100, 1]}


def push_viewer_state(viewer):
    # For state updates with callbacks,
    # Ensure the callbacks occur in the correct order
    viewer.state.update(dict(dataset_info={"source": "xarray", "id": "eraint_uvz"}))
    viewer.state.flush()
    viewer.state.update(
        dict(
            da_active="z",
        )
    )
    viewer.state.flush()
    viewer.state.update(
        dict(
            da_z="level",
            da_t="month",
            da_t_index=1,
        )
    )
    viewer.state.flush()


def assert_builder_state(builder):
    assert builder.dataset_info == {"source": "xarray", "id": "eraint_uvz"}
    assert builder.dataset is not None
    assert builder.data_array_name == "z"
    assert builder.x == "longitude"
    assert builder.y == "latitude"
    assert builder.z == "level"
    assert builder.t == "month"
    assert builder.t_index == 1


def assert_viewer_state(viewer):
    assert viewer.state.dataset_info == {"source": "xarray", "id": "eraint_uvz"}
    assert viewer.state.dataset_ready
    assert viewer.state.da_active == "z"
    assert viewer.state.da_x == "longitude"
    assert viewer.state.da_y == "latitude"
    assert viewer.state.da_z == "level"
    assert viewer.state.da_t == "month"
    assert viewer.state.da_t_index == 1
    assert viewer.state.da_size == "211 KB"
    assert viewer.state.da_vars == [
        {"name": "z", "id": 0},
        {"name": "u", "id": 1},
        {"name": "v", "id": 2},
    ]


def test_ui_state():
    viewer = DatasetViewer(server="ui", state=dict(render_auto=False))
    push_viewer_state(viewer)

    viewer._coordinate_toggle_expansion("month")
    viewer._coordinate_toggle_expansion("level")

    assert not viewer.state.ui_loading
    assert not viewer.state.ui_main_drawer
    assert not viewer.state.ui_axis_drawer
    assert viewer.state.ui_unapplied_changes
    assert viewer.state.ui_error_message is None
    assert viewer.state.ui_more_info_link is None
    assert viewer.state.ui_current_time_string == "7"
    assert viewer.state.ui_expanded_coordinates == ["month", "level"]


def test_render_options_state():
    viewer = DatasetViewer(server="render_options", state=dict(render_auto=False))
    push_viewer_state(viewer)

    viewer.set_render_scales(
        x=2,
        y=3,
        z=4,
    )
    viewer.set_render_options(
        colormap="magma",
        transparency=True,
        transparency_function="linear_r",
        scalar_warp=True,
        cartographic=False,  # not compatible with this 4D data
        # geovista GeoPlotter includes a check for GPU availability,
        # which fails on GH Actions. Disable render in this function.
        render=False,
    )

    assert viewer.state.render_x_scale == 2
    assert viewer.state.render_y_scale == 3
    assert viewer.state.render_z_scale == 4
    assert viewer.state.render_colormap == "magma"
    assert viewer.state.render_transparency
    assert viewer.state.render_transparency_function == "linear_r"
    assert viewer.state.render_scalar_warp
    assert not viewer.state.render_cartographic


def test_viewer_export():
    viewer = DatasetViewer(server="export", state=dict(render_auto=False))
    push_viewer_state(viewer)

    viewer.state.update(dict(ui_action_name="Export"))
    viewer.state.flush()

    # Export action will complete on flush and reset action state
    assert viewer.state.ui_action_name == "Export"
    assert viewer.state.ui_action_message is None
    assert viewer.state.ui_action_config_file is None

    assert viewer.state.state_export["data_origin"] == {
        "source": "xarray",
        "id": "eraint_uvz",
    }
    assert viewer.state.state_export["data_array"]["name"] == "z"
    assert viewer.state.state_export["data_array"]["x"] == "longitude"
    assert viewer.state.state_export["data_array"]["y"] == "latitude"
    assert viewer.state.state_export["data_array"]["z"] == "level"
    assert viewer.state.state_export["data_array"]["t"] == "month"
    assert viewer.state.state_export["data_array"]["t_index"] == 1
    assert viewer.state.state_export["data_slices"]["longitude"] == [0, 480, 4]
    assert viewer.state.state_export["data_slices"]["latitude"] == [0, 241, 2]
    assert viewer.state.state_export["data_slices"]["level"] == [0, 3, 1]
    assert viewer.state.state_export["data_slices"]["month"] == [0, 2, 1]
    assert not viewer.state.state_export["ui"]["main_drawer"]
    assert not viewer.state.state_export["ui"]["axis_drawer"]
    assert viewer.state.state_export["ui"]["unapplied_changes"]
    assert viewer.state.state_export["ui"]["error_message"] is None
    assert viewer.state.state_export["ui"]["more_info_link"] is None
    assert viewer.state.state_export["ui"]["expanded_coordinates"] == []
    assert viewer.state.state_export["ui"]["current_time_string"] == "7"


def test_layout():
    from trame_vuetify.ui.vuetify3 import VAppLayout

    builder = DatasetBuilder(server="layout")
    assert isinstance(builder.viewer.ui, VAppLayout)


def test_sync_to_viewer_from_builder():
    builder = DatasetBuilder(server="from_builder")
    viewer = builder.viewer
    viewer.state.render_auto = False
    push_builder_state(builder)

    assert_builder_state(builder)
    assert_viewer_state(viewer)


def test_sync_during_viewer_creation():
    builder = DatasetBuilder(server="from_creation")
    push_builder_state(builder)
    assert_builder_state(builder)

    # Viewer created last, state should sync during initialization
    viewer = builder.viewer
    viewer.state.render_auto = False
    assert_viewer_state(viewer)


def test_sync_from_viewer_ui_functions():
    builder = DatasetBuilder(server="from_ui_funcs")
    viewer = builder.viewer
    viewer.state.render_auto = False
    push_viewer_state(viewer)

    viewer._coordinate_select_axis("level", None, "da_z")
    viewer._coordinate_select_axis("month", None, "da_t")
    viewer._coordinate_change_slice("longitude", "start", 0)
    viewer._coordinate_change_slice("longitude", "stop", 90)
    viewer._coordinate_change_bounds("latitude", [0, 100])

    viewer.state.flush()
    assert_builder_state(builder)
    assert_viewer_state(viewer)
