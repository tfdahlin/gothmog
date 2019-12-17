#!/bin/bash

python3 -m venv --prompt c2server env
mkdir ./apps/files/uploaded_files
. ./env/bin/activate && pip install -r requirements.txt
