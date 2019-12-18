#!/bin/bash

python3 -m venv --prompt c2server env
[ ! -d "./apps/files/uploaded_files" ] && mkdir ./apps/files/uploaded_files
. ./env/bin/activate && pip install --upgrade pip
. ./env/bin/activate && pip install -r requirements.txt
