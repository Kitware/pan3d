#!/usr/bin/env bash
CURRENT_DIR=`dirname "$0"`

cd $CURRENT_DIR/../..
docker build -t pan3d-viewer . -f docker/Dockerfile
cd -
