#!/usr/bin/env bash
CURRENT_DIR=`dirname "$0"`

. $CURRENT_DIR/build_server.sh

cd $CURRENT_DIR/..
docker build -t pan3d-viewer .
cd -
