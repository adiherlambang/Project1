from genie.testbed import load
from netmiko import ConnectHandler
import logging
from datetime import datetime
import os
import concurrent.futures
from pyats.utils.secret_strings import to_plaintext
import time
from rich.logging import RichHandler
import csv

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
# the handler determines where the logs go: stdout/file
shell_handler = RichHandler()
file_handler = logging.FileHandler('log/CaptureInventory.log')
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
if not os.path.exists("out/CaptureInventory"):
    os.makedirs("out/CaptureInventory")

def convert_to_netmiko(device):
    netmiko_device = {}
    netmiko_device['device_type'] = "cisco_ios"
    netmiko_device['host'] = str(device.connections.cli.ip)
    netmiko_device['username'] = device.credentials.default.username
    netmiko_device['password'] = to_plaintext(device.credentials.default.password)
    netmiko_device['secret'] = to_plaintext(device.credentials.enable.password)
    return netmiko_device

def captureInventoryX(device):
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

        output = device.execute('show inventory')

    except Exception as pyats_error:
        logger.error("Failed to connect using pyats get Inventory function")
        result["message"] = "Failed to connect using pyats get Inventory function"
        result["error"] = str(pyats_error)

        try:
            netmiko_device = convert_to_netmiko(device)
            logger.info("Establishing Netmiko connection...")
            connection = ConnectHandler(**netmiko_device)
            connection.enable()
            logger.info("Connection established successfully.")
            command = "show inventory"
            output = connection.send_command(command)
        except Exception as netmiko_error:
            logger.error(f"Error connecting to device {device.name} using Netmiko: {netmiko_error}")
            result["message"] = "Failed to connect using Netmiko"
            result["error"] = str(netmiko_error)
            return result

    hostname = device.name
    logger.info(f"---getting inventory from device {hostname}---")
    waktu = datetime.now().strftime("%d-%m-%y_%H_%M_%S")
    NameFile = f"{hostname}_{waktu}.txt"
    file_path = "out/CaptureInventory/"
    file_name = os.path.join(file_path, NameFile)
    logger.info(NameFile)

    try:
        with open(file_name, 'a') as file:
            file.write(f'''{output}''')
        result["success"] = True
        result["message"] = f"Inventory captured successfully for {device.name}"
    except Exception as file_error:
        logger.error("Exception", exc_info=1)
        result["message"] = "Failed to write inventory to file"
        result["error"] = str(file_error)

    return result

def captureInventory(testbedFile):
    testbed = load(testbedFile)
    results = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(captureInventoryX, device) for device in testbed]
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

    logger.info("Get Inventory - execution completed")
    sorted_results = sorted(results, key=lambda x: x['device'])

    # Write results to CSV
    waktu = datetime.now().strftime("%d-%m-%y_%H_%M_%S")
    csv_filename = f"inventory_{waktu}.csv"
    csv_filepath = os.path.join("out", "Inventory", csv_filename)

    with open(csv_filepath, mode='w', newline='') as csvfile:
        fieldnames = ['device', 'success', 'message', 'error', 'data']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for result in sorted_results:
            writer.writerow(result)

    logger.info(f"Inventory data written to CSV file {csv_filepath}")
    return sorted_results
