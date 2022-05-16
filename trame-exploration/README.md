# Setup

Setup a working venv

```python
python3.9 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install zarr xarray vtk
pip install trame --pre
pip install jupyterlab
```

## Running

```bash
jupyter-lab
```