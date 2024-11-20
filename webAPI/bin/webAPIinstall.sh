#!/bin/bash
# webAPIrun

# Stop on errors
set -Eeuo pipefail
set -x

# Create a Python virtual environment
python3 -m venv env

# Activate Python virtual environment
source env/bin/activate

# Install back end
pip install -r requirements.txt
pip install -e .