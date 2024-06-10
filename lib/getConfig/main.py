from genie.testbed import load
from datetime import datetime
import os.path
import logging
from rich.logging import RichHandler
import concurrent.futures
from time import sleep
import time
from netmiko import ConnectHandler
from pyats.utils.secret_strings import to_plaintext

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
# the handler determines where the logs go: stdout/file
shell_handler = RichHandler()
file_handler = logging.FileHandler('log/CaptureConfig.log')
shell_handler.setLevel(logging.DEBUG)
file_handler.setLevel(logging.DEBUG)
# the formatter determines what our logs will look like
fmt_shell = '%(message)s'
fmt_file = '%(levelname)s %(asctime)s [%(filename)s:%(funcName)s:%(lineno)d] %(message)s'

shell_formatter = logging.Formatter(fmt_shell)
file_formatter = logging.Formatter(fmt_file)

# here we hook everything together
shell_handler.setFormatter(shell_formatter)
file_handler.setFormatter(file_formatter)
logger.addHandler(shell_handler)
logger.addHandler(file_handler)


# Check if output folder is available, create it if not
if not os.path.exists("out/CaptureConfig"):
    os.makedirs("out/CaptureConfig")

def convert_to_netmiko(device):
    netmiko_device = {}
    netmiko_device['device_type'] = "cisco_ios"
    netmiko_device['host'] = str(device.connections.cli.ip)
    netmiko_device['username'] = device.credentials.default.username
    netmiko_device['password'] = to_plaintext(device.credentials.default.password)
    netmiko_device['secret'] = to_plaintext(device.credentials.enable.password)
    return netmiko_device

def captureConfigX(device):
    result = {
        "device": device.name,
        "success": False,
        "message": "",
        "error": ""
    }

    try:
        attempt = 1
        retry = 0
        mx_retry = 3
        while retry < mx_retry:
            try:
                device.connect(learn_hostname=True, learn_os=True, log_stdout=False, mit=True)
                break
            except Exception as conn_error:
                retry += 1
                attempt += 1
                if retry < mx_retry:
                    logger.warning(f"Connection attempt {retry}/{mx_retry} failed for {device.name} ({device.connections.cli.ip}): {conn_error}")
                    logger.info("Retrying in 2 seconds...")
                    time.sleep(2)
                else:
                    logger.error(f"Failed to establish connection to {device.name} ({device.connections.cli.ip}) after {mx_retry} attempts.")
                    result["message"] = f"Failed to establish connection after {mx_retry} attempts."
                    result["error"] = str(conn_error)
                    return result

        output = device.execute('show running-config')

    except Exception as pyats_error:
        logger.error("Failed to connect using pyats get Config function")
        result["message"] = "Failed to connect using pyats get Config function"
        result["error"] = str(pyats_error)

        try:
            netmiko_device = convert_to_netmiko(device)
            logger.info("Establishing Netmiko connection...")
            connection = ConnectHandler(**netmiko_device)
            connection.enable()
            logger.info("Connection established successfully.")
            command = "show running-config"
            output = connection.send_command(command)
        except Exception as netmiko_error:
            logger.error(f"Error connecting to device {device.name} using Netmiko: {netmiko_error}")
            result["message"] = "Failed to connect using Netmiko"
            result["error"] = str(netmiko_error)
            return result

    hostname = device.name
    logger.info(f"---getting capture config from device {hostname}---")
    waktu = datetime.now().strftime("%d-%m-%y_%H_%M_%S")
    NameFile = f"{hostname}_{waktu}.txt"
    file_path = "out/CaptureConfig/"
    file_name = os.path.join(file_path, NameFile)
    logger.info(NameFile)

    try:
        with open(file_name, 'a') as file:
            file.write(f'''{output}''')
        result["success"] = True
        result["message"] = f"Configuration captured successfully for {device.name}"
    except Exception as file_error:
        logger.error("Exception", exc_info=1)
        result["message"] = "Failed to write configuration to file"
        result["error"] = str(file_error)

    return result


def captureConfig(testbedFile):
    testbed = load(testbedFile)
    results = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(captureConfigX, device) for device in testbed]
        logger.info("Connecting to devices...")
        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result()
                results.append(result)
                if not result["success"]:
                    logger.error(f"Error with device {result['device']}: {result['message']}, Error: {result['error']}")
            except Exception as exc:
                error_message = f"Exception occurred: {str(exc)}"
                logger.error(error_message)
                results.append({"device": "Unknown", "success": False, "message": error_message, "error": str(exc)})

    logger.info("Get Config - execution completed")
    return results
