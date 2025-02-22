# Setup Instructions

## Setup Instructions

1. [Setup Virtual Environment](/resources/docs/setup/virtualenv.md)

1. Configure all etc files [here](/etc)

    1. [Populate AND rename your ```config.yaml``` file](/etc/template_config.yaml)

    1. [Populate AND rename your ```server_service_inventory.yaml``` file](/etc/template_server_service_inventory.yaml)

    1. [Populate AND rename your ```servers.yaml``` file](/etc/template_servers.yaml)

    1. [Populate AND rename your ```service_manager.yaml``` file](/etc/template_service_manager.yaml)

1. Propagate SSH Keys

    ```bash
    . ./scripts/ssh_key_manager.sh
    ```

1. [Ensure sudoers file is up to date](/resources/docs/setup/sudoers.md)