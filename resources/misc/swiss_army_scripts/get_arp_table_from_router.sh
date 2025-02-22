#!/bin/bash

# Vars, exports
PYTHONPATH="/opt/apps/observius"
export PYTHONPATH

# Activate the virtual environment
source /opt/apps/observius/venv/bin/activate

# Run the Python script
python /opt/apps/observius/scripts/swiss/get_arp_table_from_router.py "$@"
