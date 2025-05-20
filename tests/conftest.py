from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def vtr_path():
    return str((Path(__file__).with_name("data") / "air_temperature.vtr").resolve())


@pytest.fixture(scope="session")
def vts_path():
    return str((Path(__file__).with_name("data") / "structured.vts").resolve())


@pytest.fixture(scope="session")
def vti_path():
    return str((Path(__file__).with_name("data") / "wavelet.vti").resolve())
