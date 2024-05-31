import csv
import datetime
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

EOF = False
count_iface_up = 0
count_iface_down = 0
timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

# devices = []
# Check if output folder is available, create it if not
if not os.path.exists("out/InterfaceListedCRC"):
    os.makedirs("out/InterfaceListedCRC")
    
def interfaceListedCRC(device,counter):
    try:
        logger.info("Establishing Netmiko connection...")
        connection = ConnectHandler(**device)
        logger.info("Connection established successfully.")
        
        command = "show interface"
        logger.info(f"Sending command {command} to {device}")
        output = connection.send_command(command,read_timeout=500)
        
        with open('lib/getCRC/nxos_show_interface_custom.template') as template:
            template = textfsm.TextFSM(template)

        parsed_output = template.ParseText(output)

        # Create a dictionary
        result_dict = {}
        
        check=['.','mgmt0']
        
        # Iterate through the data and convert it into a dictionary
        for item in parsed_output:
            #logger.info(item)
            result_dict["INTERFACE"] = item[0]
            if any(dot in result_dict["INTERFACE"] for dot in check):
                logger.info(f"Skip subInterface for device: {device.name}")
            else:    
                if item[3]!='' or item[5]!='' or item[4]!='':
                    result_dict["INPUT_ERRORS"] = int(item[3])
                    result_dict["OUTPUT_ERRORS"] = int(item[5])
                    result_dict["CRC"] = int(item[4])
                else:
                    result_dict["INPUT_ERRORS"] = 0
                    result_dict["OUTPUT_ERRORS"] = 0
                    result_dict["CRC"] = 0
                #logger.info(result_dict)

                interface =result_dict["INTERFACE"]
                crc = result_dict["CRC"]
                input_errors = result_dict["INPUT_ERRORS"]
                output_errors = result_dict["OUTPUT_ERRORS"]
            
                with open(
                f"out/InterfaceCRC/show_intList_crc_{timestamp}.csv", "a", newline=""
                ) as csvfile:
                    writer = csv.writer(csvfile)  
                    writer.writerow([counter,device.name,interface,crc,input_errors,output_errors])
                if crc > 0 or input_errors > 0 or output_errors > 0:
                        with open(
                        f"out/InterfaceCRC/found_intList_crc_{timestamp}.csv", "a", newline=""
                        ) as csvfile:
                            writer = csv.writer(csvfile)  
                            writer.writerow([counter,device.name,interface,crc,input_errors,output_errors])
    except Exception as exc:
        logger.error(exc)
        raise Exception(f"Finish getting CRC from interface device listed with an Error") 
                        
def convert_to_netmiko(device):
    netmiko_devices = []
    # print(device)
    with open(device) as f:
        devices = yaml.safe_load(f)['devices']
        # print(devices)
        for device_name,device_info in devices.items():
            netmiko_device = {}
            # netmiko_device['name'] = device_name 
            
            if device_info['os']=='ios':
                netmiko_device['device_type'] = "cisco_ios"
            elif device_info['os']=='iosxe':
                netmiko_device['device_type'] = "cisco_iosxe"
            elif device_info['os']=='nxos':
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
    testbed = convert_to_netmiko(testbedFile)              
    futures = []
    counter = 1
    
    # print(testbed)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        for device in testbed:
            # print(device['name'])
            futures.append(executor.submit(interfaceListedCRC, device, counter))
            counter += 1
            sleep(0.1)
        # Wait for all futures to complete
    for future in concurrent.futures.as_completed(futures):
        try:
            future.result()
        except Exception as exc:
            # logger.error(f"{exc} occurred while processing device {device['host']}")
            return str(exc)

    logger.info("Script execution completed successfully.")