from netmiko import ConnectHandler
import logging

logging.basicConfig(filename="netmiko.log", level=logging.DEBUG)
logger = logging.getLogger("netmiko")


def run_commands_on_host(host, username, password, device_type, commands):
    """
    Connects to a network device and runs a list of commands.
    Args:
        host (str): The IP address or hostname of the device.
        username (str): The username to authenticate with.
        password (str): The password to authenticate with.
        device_type (str): The type of the device (e.g., 'cisco_ios').
        commands (list): A list of commands to run on the device.
    Returns:
        list: A list of strings containing the output of each command.
    """
    device = {
        "device_type": device_type,
        "host": host,
        "username": username,
        "password": password,
    }

    try:
        connection = ConnectHandler(**device)
        output = []
        for command in commands:
            logger.debug(f"Executing command: {command}")
            command_output = connection.send_command(command)
            logger.debug(f"Command output: {command_output}")
            output.extend(command_output.splitlines())
        connection.disconnect()
        return output
    except Exception as e:
        logger.error(f"Error: {e}")
        raise
