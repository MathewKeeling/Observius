#!/bin/bash

# Vars, exports
PYTHONPATH="/opt/apps/observius"
export PYTHONPATH

# Activate the virtual environment
source /opt/apps/observius/venv/bin/activate

# Run the Python script
python /opt/apps/observius/scripts/swiss/opennms_retrieve_interfaces.py "$@"
