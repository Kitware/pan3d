#!/bin/bash
mkdir -p /home/jovyan/shared/pan3d_examples
ln -sf /shared/pan3d_examples /home/jovyan/shared/pan3d_examples
exec "$@"
