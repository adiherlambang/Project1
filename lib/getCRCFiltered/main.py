import csv
from genie.testbed import load
from datetime import datetime
import concurrent.futures
from time import sleep
import logging
from rich.logging import RichHandler
from rich.console import Console
import os
import textfsm
from netmiko import ConnectHandler
from pyats.utils.secret_strings import to_plaintext
import yaml
import time

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
# the handler determines where the logs go: stdout/file
shell_handler = RichHandler()
file_handler = logging.FileHandler('log/InterfaceListed-CRC.log')
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

timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

hostname = ''
# Check if output folder is available, create it if not
if not os.path.exists("out/Capture_InterfaceCRC-Filtered"):
    os.makedirs("out/Capture_InterfaceCRC-Filtered")
    
def interfaceListedCRC(device,testbedFile):
    result = {
        "device": device.name,
        "success": False,
        "message": "",
        "error": "",
        "data": None
    }

    get_ifce=[]
    
    try:
        attempt = 1
        retry = 0
        mx_retry = 1
        while retry < mx_retry:
            try:
                logger.info(f"Connecting to Device: {device.name}")
                device.connect(learn_hostname=True, learn_os=True, log_stdout=False, mit=True, timeout=10)
                logger.info(f"Successfully Connected to Device: {device.name}")
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
        
        logger.info(f"Device: {device.name}, Parsing data with Pyats")
        if device.type=='nxos' :
            output_iface_crc = device.parse('show interface', timeout=300)
        else:
            output_iface_crc = device.parse('show interfaces', timeout=300)
        crc_interface=[]
        # logger.info(output_iface_crc)
        # logger.info(device)
        with open(testbedFile, 'r') as f:
            testbed_data = yaml.safe_load(f)
        
        for device_name, device_data in testbed_data['topology'].items():
            logger.info(f"Device: {device_name}")
            interfaces = device_data.get('interfaces', {})

            for intf_name, intf_details in interfaces.items():
                # logger.info(f"Interface: {intf_name}")
                get_ifce.append(intf_name)
            logger.info(f"Get Interface: {get_ifce}")
            
        iface_skipp = ['.']
        for index, (key, value) in enumerate(output_iface_crc.items(), start=1):
            if any(sub == element for sub in get_ifce for element in key.split()):
                if any(sub1 in key for sub1 in iface_skipp):
                    logger.info(f"Skipping interface: {key}. in hostname: {device}")
                    continue
                else:
                    crc = output_iface_crc[key]['counters']['in_crc_errors']
                    input_errors = output_iface_crc[key]['counters']['in_errors']
                    output_errors = output_iface_crc[key]['counters']['out_errors']
                    # logger.info(f"interface: {key},CRC{crc},in_error{input_errors},out_error{output_errors}")
                    crc_interface.append({
                        'No_Interface': index,
                        'Interface': key,
                        'CRC': crc,
                        'Input_Errors': input_errors,
                        'Output_Errors': output_errors
                    })
        
        # logger.info(f"Result Interface CRC: {crc_interface}")
        result["data"] = crc_interface
        result["success"] = True
        return result
    
    except Exception as pyats_error:
        logger.error("Failed to connect using pyats get CRC interface function")
        result["message"] = "Failed to connect using pyats get CRC interface function"
        result["error"] = str(pyats_error)
                        
def convert_to_netmiko(device):
    netmiko_devices = []
    # print(device)
    with open(device) as f:
        devices = yaml.safe_load(f)['devices']
        # print(devices)
        for device_name,device_info in devices.items():
            netmiko_device = {}
            # hostname = device_name
            
            if device.os=='ios':
                netmiko_device['device_type'] = "cisco_ios"
            elif device.os=='iosxe':
                netmiko_device['device_type'] = "cisco_xe"
            elif device.os=='iosxr':
                netmiko_device['device_type'] = "cisco_xr"    
            elif device.os=='nxos':
                netmiko_device['device_type'] = "cisco_nxos"
               
            netmiko_device['host'] = str(device_info['connections']['cli']['ip'])
            netmiko_device['username'] = device_info['credentials']['default']['username']
            netmiko_device['password'] = to_plaintext(device_info['credentials']['default']['password'])
            netmiko_device['secret'] = to_plaintext(device_info['credentials']['enable']['password'])
            if device_info['connections']['cli']['protocol'] == 'telnet':
                netmiko_device['port'] = '21'
            else:
                netmiko_device['port'] = '22'
            netmiko_devices.append(netmiko_device)
        return netmiko_devices

def main_InterfaceCRC(testbedFile):
    # testbed = convert_to_netmiko(testbedFile)
    testbed = load(testbedFile)
    crc_iface_list = []
    # counter = 1
    results = []
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(interfaceListedCRC, device, testbedFile) for device in testbed]
        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result()
                results.append(result)
                if result["success"]:
                    # logger.info(result)
                    crc_iface_list.append({"Hostname": result["device"], "data": result["data"]})
                else:
                    logger.error(f"Error with device {result['device']}: {result['message']}, Error: {result['error']}")
            except Exception as exc:
                error_message = f"Exception occurred: {str(exc)}"
                logger.error(error_message)
                results.append({"device": "Unknown", "success": False, "message": error_message, "error": str(exc)})
                
    crc_iface_list.sort(key=lambda x: x['Hostname'])
    waktu = datetime.now().strftime("%d-%m-%y_%H_%M_%S")
    csv_filename = f"CaptureCRC-Filtered_{waktu}.csv"
    csv_filepath = os.path.join("out", "Capture_InterfaceCRC-Filtered", csv_filename)
    
    with open(csv_filepath, mode='w', newline='') as csvfile:
        fieldnames = ['No_Hostname', 'Hostname', 'Interface', 'CRC', 'Input_Errors', 'Output_Errors']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        hostname_counter = 1
        for item in crc_iface_list:
            hostname = item["Hostname"]
            data = item["data"]
            for interface in data:
                row = {
                    'No_Hostname': hostname_counter,
                    'Hostname': hostname,
                    'Interface': interface['Interface'],
                    'CRC': interface['CRC'],
                    'Input_Errors' : interface['Input_Errors'],
                    'Output_Errors': interface['Output_Errors']
                }
                writer.writerow(row)
            hostname_counter += 1
            
    logger.info(f"Interface CRC data written to CSV file")
    logger.info(f"Result Interface CRC: {results}")
    return results    
    # print(testbed)

    # with concurrent.futures.ThreadPoolExecutor() as executor:
    #     for device in testbed:
    #         # print(device['name'])
    #         futures.append(executor.submit(interfaceListedCRC, device, counter))
    #         counter += 1
    #         sleep(0.1)
    #     # Wait for all futures to complete
    # for future in concurrent.futures.as_completed(futures):
    #     try:
    #         future.result()
    #     except Exception as exc:
    #         logger.error(f"{exc} occurred while processing device {hostname}")
    #         return str(exc)

    # logger.info("Script execution completed successfully.")