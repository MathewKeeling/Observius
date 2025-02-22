# SSH Key Manager

## Overview

Several Servers require the automation server to have its SSH keys placed on the target server for implicit authorization.

Here is an overview on how to do that.

**You must populate your ```servers.yaml``` file before proceeding**

```
# cd to installation directory
cd /opt/apps/insrt

# activate virtual environment
. ./venv/bin/activate

# run the script
. ./resources/docs/ssh_key_manager.py
```