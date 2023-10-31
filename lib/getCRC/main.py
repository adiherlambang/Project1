from pyats.topology import loader
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

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
# the handler determines where the logs go: stdout/file
shell_handler = RichHandler()
file_handler = logging.FileHandler('log/Interface-CRC.log')
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
timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')

# Check if output folder is available, create it if not
if not os.path.exists("out/InterfaceCRC"):
    os.makedirs("out/InterfaceCRC")

def proc_iface_crc_ios(device,counter):
    try:
        device.connect(learn_hostname = True, learn_os = True, log_stdout=False,mit=True)
        logger.info(f"Device: {device.name}")
        output_iface_crc = device.parse('show interface')
        for iface in output_iface_crc:
            if "Ethernet" in iface:
                crc = output_iface_crc[iface]['counters']['in_crc_errors']
                input_errors = output_iface_crc[iface]['counters']['in_errors']
                output_errors = output_iface_crc[iface]['counters']['out_errors']
                with open(
                f"out/InterfaceCRC/show_int_crc_{timestamp}.csv", "a", newline=""
                ) as csvfile:
                    writer = csv.writer(csvfile)  
                    writer.writerow([counter,device.name,iface,crc,input_errors,output_errors])
                if crc > 0 or input_errors > 0 or output_errors > 0:
                    with open(
                    f"out/InterfaceCRC/found_int_crc_{timestamp}.csv", "a", newline=""
                    ) as csvfile:
                        writer = csv.writer(csvfile)  
                        writer.writerow([counter,device.name,iface,crc,input_errors,output_errors])
   
    except Exception as e:
        logger.error(f"Error connecting to device {device.name}: {e}")


def proc_iface_crc_xe(device,counter):
    try:
        device.connect(learn_hostname = True, learn_os = True, log_stdout=False,mit=True)
        logger.info(f"Device: {device.name}")
        output_iface_crc = device.parse('show interfaces')
        for iface in output_iface_crc:
            crc = output_iface_crc[iface]['counters']['in_crc_errors']
            input_errors = output_iface_crc[iface]['counters']['in_errors']
            output_errors = output_iface_crc[iface]['counters']['out_errors']
            with open(
            f"out/InterfaceCRC/show_int_crc_{timestamp}.csv", "a", newline=""
            ) as csvfile:
                writer = csv.writer(csvfile)  
                writer.writerow([counter,device.name,iface,crc,input_errors,output_errors])
            if crc > 0 or input_errors > 0 or output_errors > 0:
                    with open(
                    f"out/InterfaceCRC/found_int_crc_{timestamp}.csv", "a", newline=""
                    ) as csvfile:
                        writer = csv.writer(csvfile)  
                        writer.writerow([counter,device.name,iface,crc,input_errors,output_errors])  
    except Exception as e:
        logger.error(f"Error connecting to device {device.name}: {e}")

def proc_iface_crc_xr(device,counter):
    try:
        device.connect(learn_hostname = True, learn_os = True, log_stdout=False,mit=True)
        print(f"Device: {device.name}")
        output_iface_crc = device.parse('show interfaces')
        for iface in output_iface_crc:
            if iface == 'Null0':
                print('Iface Null')
            else:
                crc = output_iface_crc[iface]['counters']['in_crc_errors']
                input_errors = output_iface_crc[iface]['counters']['in_errors']
                output_errors = output_iface_crc[iface]['counters']['out_errors']
                with open(
                f"out/InterfaceCRC/show_int_crc_{timestamp}.csv", "a", newline=""
                ) as csvfile:
                    writer = csv.writer(csvfile)  
                    writer.writerow([counter,device.name,iface,crc,input_errors,output_errors])
                if crc > 0 or input_errors > 0 or output_errors > 0:
                        with open(
                        f"out/InterfaceCRC/found_int_crc_{timestamp}.csv", "a", newline=""
                        ) as csvfile:
                            writer = csv.writer(csvfile)  
                            writer.writerow([counter,device.name,iface,crc,input_errors,output_errors])  
                
    except Exception as e:
        logger.error(f"Error connecting to device {device.name}: {e}")

def proc_iface_crc_nx(device,counter):
    try:
        logger.info("nxos")
        device.connect(learn_hostname = True, learn_os = True, log_stdout=False, mit=True)
        logger.info(f"Device: {device.name}")
        output_iface_crc = device.parse('show interface')
        for iface in output_iface_crc:
            #logger.info(output_iface_crc)
            if 'Ethernet' in iface:           
                #logger.info(output_iface_crc[iface]['counters']['out_errors'])
                crc = output_iface_crc[iface]['counters']['in_crc_errors']
                input_errors = output_iface_crc[iface]['counters']['in_errors']
                output_errors = output_iface_crc[iface]['counters']['out_errors']
                #logger.info(f"{crc},{input_errors},{output_errors}")
                with open(
                f"out/InterfaceCRC/show_int_crc_{timestamp}.csv", "a", newline=""
                ) as csvfile:
                    writer = csv.writer(csvfile)  
                    writer.writerow([counter,device.name,iface,crc,input_errors,output_errors])
                if crc > 0 or input_errors > 0 or output_errors > 0:
                        with open(
                        f"out/InterfaceCRC/found_int_crc_{timestamp}.csv", "a", newline=""
                        ) as csvfile:
                            writer = csv.writer(csvfile)  
                            writer.writerow([counter,device.name,iface,crc,input_errors,output_errors])  

    except :
        logger.error(f"Error get CRC for device {device.name}")
        runNetmiko(device,counter)

def convert_to_netmiko(device):
    netmiko_device = {}
    if device.os=='ios':
        netmiko_device['device_type'] = "cisco_ios"
    elif device.os=='iosxe':
        netmiko_device['device_type'] = "cisco_iosxe"
    elif device.os=='nxos':
        netmiko_device['device_type'] = "cisco_nxos"
    netmiko_device['host'] = str(device.connections.cli.ip)
    netmiko_device['username'] = device.credentials.default.username
    netmiko_device['password'] = to_plaintext(device.credentials.default.password)
    netmiko_device['secret'] = to_plaintext(device.credentials.enable.password)
    return netmiko_device

def runNetmiko(device,counter):
    logger.error("Retrying connect to device with netmiko")
    # Convert the device to Netmiko format
    netmiko_device = convert_to_netmiko(device)

    #Establish the Netmiko connection
    logger.info("Establishing Netmiko connection...")
    connection = ConnectHandler(**netmiko_device)
    logger.info("Connection established successfully.")

    # Send a command and retrieve the output
    command = "show interface"
    logger.info(f"Sending command {command} to {device}")
    output = connection.send_command(command,read_timeout=300)

    with open('lib/getCRC/nxos_show_interface_custom.template') as template:
        template = textfsm.TextFSM(template)

    parsed_output = template.ParseText(output)

        # Create a dictionary
    result_dict = {}

# Iterate through the data and convert it into a dictionary
    for item in parsed_output:
        #logger.info(item)
        result_dict["INTERFACE"] = item[0]
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
        f"out/InterfaceCRC/show_int_crc_{timestamp}.csv", "a", newline=""
        ) as csvfile:
            writer = csv.writer(csvfile)  
            writer.writerow([counter,device.name,interface,crc,input_errors,output_errors])
        if crc > 0 or input_errors > 0 or output_errors > 0:
                with open(
                f"out/InterfaceCRC/found_int_crc_{timestamp}.csv", "a", newline=""
                ) as csvfile:
                    writer = csv.writer(csvfile)  
                    writer.writerow([counter,device.name,interface,crc,input_errors,output_errors])  


def interfaceCRC(testbedFile):
    testbed= loader.load(testbedFile)
    with open(f'out/InterfaceCRC/show_int_crc_{timestamp}.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['No','Hostname','Interface', 'CRC', 'Input Errors', 'Output Errors'])
        
    with open(f'out/InterfaceCRC/found_int_crc_{timestamp}.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['No','Hostname','Interface', 'CRC', 'Input Errors', 'Output Errors'])

                
    futures = []
    counter = 1

    with concurrent.futures.ThreadPoolExecutor() as executor:
        for device in testbed:
            if device.type == 'iosxe':
                futures.append(executor.submit(proc_iface_crc_xe, device, counter))
                counter += 1
                sleep(0.1)
            elif device.type == 'iosxr':
                futures.append(executor.submit(proc_iface_crc_xr, device, counter))
                counter += 1
                sleep(0.1)
            elif device.type == 'nxos':
                futures.append(executor.submit(proc_iface_crc_nx, device, counter))
                counter += 1
                sleep(0.1)
            elif device.type == 'ios':
                futures.append(executor.submit(proc_iface_crc_ios, device, counter))
                counter += 1
                sleep(0.1)
        # Wait for all futures to complete
    for future in concurrent.futures.as_completed(futures):
        try:
            future.result()
        except Exception as exc:
            logger.info(f"{exc} occurred while processing device {device.name}")

    logger.info("Script execution completed successfully.")

