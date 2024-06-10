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

def parse_inventory(output):
    inventory = []
    lines = output.splitlines()
    for line in lines:
        if 'NAME' in line and 'PID' in line and 'SN' in line:
            fields = line.split()
            name_index = fields.index('NAME')
            pid_index = fields.index('PID')
            sn_index = fields.index('SN')
            break

    for line in lines:
        if 'NAME:' in line and 'PID:' in line and 'SN:' in line:
            parts = line.split('NAME:')[1].split('PID:')
            name = parts[0].strip().strip('"')
            parts = parts[1].split('SN:')
            pid = parts[0].strip()
            sn = parts[1].strip()
            inventory.append({'Name': name, 'PID': pid, 'SN': sn})

    return inventory

def captureInventoryX(device):
    result = {
        "device": device.name,
        "success": False,
        "message": "",
        "error": "",
        "data": None
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

        output = device.parse('show inventory')
        inventory_data = []

        for index, (key, value) in enumerate(output.items(), start=1):
            inventory_data.append({
                'No_Inventory': index,
                'Name': value.get('name', ''),
                'PID': value.get('pid', ''),
                'SN': value.get('sn', '')
            })
        
        result["data"] = inventory_data
        result["success"] = True
        result["message"] = f"Inventory captured successfully for {device.name}"

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
            inventory_data = parse_inventory(output)
            result["data"] = inventory_data
            result["success"] = True
            result["message"] = f"Inventory captured successfully for {device.name}"
        except Exception as netmiko_error:
            logger.error(f"Error connecting to device {device.name} using Netmiko: {netmiko_error}")
            result["message"] = "Failed to connect using Netmiko"
            result["error"] = str(netmiko_error)
            return result

    return result

def captureInventory(testbedFile):
    testbed = load(testbedFile)
    results = []
    inventory_list = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(captureInventoryX, device) for device in testbed]
        logger.info("Connecting to devices...")
        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result()
                results.append(result)
                if result["success"]:
                    print(result)
                    inventory_list.append({"Hostname": result["device"], "data": result["data"]})
                else:
                    logger.error(f"Error with device {result['device']}: {result['message']}, Error: {result['error']}")
            except Exception as exc:
                error_message = f"Exception occurred: {str(exc)}"
                logger.error(error_message)
                results.append({"device": "Unknown", "success": False, "message": error_message, "error": str(exc)})

    # Sort inventory by device name
    inventory_list.sort(key=lambda x: x['Hostname'])

    # Write inventory to CSV
    waktu = datetime.now().strftime("%d-%m-%y_%H_%M_%S")
    csv_filename = f"CaptureInventory_{waktu}.csv"
    csv_filepath = os.path.join("out", "CaptureInventory", csv_filename)

    with open(csv_filepath, mode='w', newline='') as csvfile:
        fieldnames = ['No_Hostname', 'Hostname', 'No_Inventory', 'Name', 'PID', 'SN']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        hostname_counter = 1
        for item in inventory_list:
            print(item["data"])
            hostname = item["Hostname"]
            data = item["data"]
            inventory_counter = 1
            for inventory in data:
                row = {
                    'No_Hostname': hostname_counter,
                    'Hostname': hostname,
                    'No_Inventory': inventory_counter,
                    'Name': inventory['Name'],
                    'PID': inventory['PID'],
                    'SN': inventory['SN']
                }
                writer.writerow(row)
                inventory_counter += 1
            hostname_counter += 1

    logger.info(f"Inventory data written to CSV file {csv_filepath}")
    return results

