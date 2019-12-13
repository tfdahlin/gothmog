#!/bin/bash
# Create the applications virtual environment
python3 -m venv --prompt c2client env
# Install necessary libraries
. env/bin/activate && pip install -r requirements.txt
