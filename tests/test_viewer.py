from pan3d.viewers.preview import XArrayViewer


def assert_builder_state(builder):
    assert builder.state.get("data_origin") == {
        "source": "xarray",
        "id": "eraint_uvz",
        "order": "C",
    }
    assert builder.arrays == ["z"]
    assert builder.x == "longitude"
    assert builder.y == "latitude"
    assert builder.z == "level"
    assert builder.t == "month"
    assert builder.t_index == 1


def test_ui_state():
    viewer = XArrayViewer(server="test")

    # fake server started to trigger callback
    viewer.state.ready()
    viewer.disable_rendering = True

    viewer.import_state(
        {
            "data_origin": {"source": "xarray", "id": "eraint_uvz"},
            "dataset_config": {
                "arrays": ["z"],
                "t_index": 1,
                "slices": {
                    "longitude": [0, 90, 1],
                    "latitude": [0, 100, 1],
                },
            },
        }
    )
    assert_builder_state(viewer.source)
    assert viewer.state.axis_names == ["longitude", "latitude", "level"]
    assert viewer.state.data_origin_error is False
    assert viewer.state.data_origin_source == "xarray"
    assert viewer.state.data_origin_id == "eraint_uvz"
    assert viewer.state.load_button_text == "Loaded"
    assert viewer.state.can_load is False
    assert viewer.state.show_data_information is True
    assert len(viewer.state.t_labels) == 2


def test_render_options_state():
    viewer = XArrayViewer(server="render_options")

    # fake server started to trigger callback
    viewer.state.ready()
    viewer.disable_rendering = True

    viewer.import_state(
        {
            "data_origin": {"source": "xarray", "id": "eraint_uvz"},
            "dataset_config": {
                "arrays": ["z"],
                "t_index": 1,
            },
        }
    )
    with viewer.state:
        viewer.state.update(
            {
                "scale_x": 0.1,
                "scale_y": 0.2,
                "scale_z": 0.3,
                "color_by": "z",
            }
        )

    assert_builder_state(viewer.source)
    assert viewer.actor.GetScale() == (0.1, 0.2, 0.3)
    assert viewer.mapper.array_name == "z"
