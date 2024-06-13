import os
import csv
from datetime import datetime
import concurrent.futures
from time import sleep
from pyats.topology.loader import load
import logging
from rich.logging import RichHandler
from pyats.utils.secret_strings import to_plaintext
import textfsm
from netmiko import ConnectHandler
import time

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
# the handler determines where the logs go: stdout/file
shell_handler = RichHandler()
file_handler = logging.FileHandler('log/getMemmoryUtils.log')
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
if not os.path.exists("out/Capture_Memmory_Utilization"):
    os.makedirs("out/Capture_Memmory_Utilization")

# timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

def convert_to_netmiko(device):
    netmiko_device = {}
    netmiko_device['device_type'] = "cisco_ios"
    netmiko_device['host'] = str(device.connections.cli.ip)
    netmiko_device['username'] = device.credentials.default.username
    netmiko_device['password'] = to_plaintext(device.credentials.default.password)
    netmiko_device['secret'] = to_plaintext(device.credentials.enable.password)
    return netmiko_device

#Function to sorted data
# def sort_csv_by_field(input_file, sort_field):
#     data = []
    
#     # Read the data from the input CSV file
#     with open(input_file, "r", newline="") as csvfile:
#         reader = csv.DictReader(csvfile)
#         data = list(reader)

#     # Sort the data based on the specified field
#     sorted_data = sorted(data, key=lambda x: int(x.get(sort_field, 0)))

#     # Write the sorted data back to the input CSV file
#     with open(input_file, "w", newline="") as csvfile:
#         fieldnames = sorted_data[0].keys() if sorted_data else []
#         writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
#         writer.writeheader()
#         writer.writerows(sorted_data)
        
def getMemmoryInfo(device):
    result = {
        "device": device.name,
        "success": False,
        "message": "",
        "error":"",
        'data':None
    }
    
    output = ''
    
    try:
        attempt = 1
        retry = 0
        mx_retry = 3
        
        while retry < mx_retry:
            try:
                logger.info(f"Connecting to Device: {device.name}")
                device.connect(learn_hostname=True, learn_os=True, log_stdout=True, mit=True, timeout=120)
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
                    result["error"] = str(conn_error)
                    return result
            
        if device.type == 'iosxe':
            logger.info(f"Device: {device.name}, with OS type: {device.type}")
            output = device.parse("show processes memory")
            logger.info(output)
            used = round(output['processor_pool']['used']/1024/1000, 2)
            total = round(output['processor_pool']['total']/1024/1000, 2)
            percentage = round(used / total * 100, 2)
            
            # Categorize percentage based on certain ranges
            if percentage <= 40:
                category = "low"
            elif percentage <= 70:
                category = "medium"
            elif percentage <= 85:
                category = "high"
            else:
                category = "critical"
                
            memmory_data = []
            
            for index, (key, value) in enumerate(output.items(), start=1):
                memmory_data.append({
                    'No':index,
                    'Hostname':device.name,
                    'Usage':used,
                    'Total':total,
                    'Percentage':percentage,
                    'Category':category
                })
            
            result["data"] = memmory_data
            result["success"] = True
            result["message"] = f"Memmory utilization captured successfully for {device.name}"
                
        elif device.type == 'iosxr':
            
            output = device.parse("show watchdog memory-state")
        elif device.type == 'ios':
            
            output = device.parse("show processes memory")
        elif device.type == 'nxos':
            
            logger.info(f"Device: {device.name}, with OS type: {device.type}")
            output = device.parse("show system resources")
            logger.info(output)
            
            return result
            
            # used = round(output["memory_usage"]["memory_usage_used_kb"]/1024, 2)
            # total = round(output["memory_usage"]["memory_usage_total_kb"]/1024, 2)
            # percentage = round(used / total * 100, 2)

            # Categorize percentage based on certain ranges
            # if percentage <= 40:
            #     category = "low"
            # elif percentage <= 70:
            #     category = "medium"
            # elif percentage <= 85:
            #     category = "high"
            # else:
            #     category = "critical"
                
            # memmory_data = []
            
            # for index, (key, value) in enumerate(output.items(), start=1):
            #     memmory_data.append({
            #         'No':index,
            #         'Hostname':device.name,
            #         'Usage':used,
            #         'Total':total,
            #         'Percentage':percentage,
            #         'Category':category
            #     })
            
            # result["data"] = memmory_data
            # result["success"] = True
            # result["message"] = f"Memmory utilization captured successfully for {device.name}"
            
        else :
            result["success"] = False
            result["error"] = "Not Compatible device OS version"
            return result               
            
    except Exception as pyats_error:
        logger.error("Failed to parse using pyats get Memmory Utilization function")
        result["error"] = str(pyats_error)
    return result

# def get_iosxe_memory_info(device, counter):
#     result["device"] = device.name
#     try:
#         try:
#             attempt = 1
#             retry = 0
#             mx_retry = 3
#             while retry < mx_retry:
#                 try:
#                     logger.info(f"Connecting to Device: {device.name}")
#                     device.connect(learn_hostname = True, learn_os = True, log_stdout=False,mit=True)
#                     logger.info(f"Successfully Connected to Device: {device.name}")
#                     break
#                 except Exception as conn_error:
#                         retry += 1
#                         attempt +=1
#                         if retry < mx_retry:
#                             logger.error(f"Connection attempt {retry}/{mx_retry} failed for {device.name} ({device.connections.cli.ip}): {conn_error}")
#                             logger.info(f"Retrying in 1 seconds...")
#                             time.sleep(2)
#                         else:
#                             logger.error(f"Failed to establish connection to {device.name} ({device.connections.cli.ip}) after {mx_retry} attempts.")
#                             result["error"] = str(conn_error)
#                             break  # Exit the loop after max retries
                        
#             # Print the output
#             output = device.parse("show processes memory")

#             used = round(output['processor_pool']['used']/1024/1000, 2)
#             total = round(output['processor_pool']['total']/1024/1000, 2)
#             percentage = round(used / total * 100, 2)

#             # Categorize percentage based on certain ranges
#             if percentage <= 40:
#                 category = "low"
#             elif percentage <= 70:
#                 category = "medium"
#             elif percentage <= 85:
#                 category = "high"
#             else:
#                 category = "critical"

#             result["success"] = True

#             # Write the output to the CSV file
#             with open(
#                 f"out/Capture_Memmory_Utilization/Memmory_{timestamp}.csv", "a", newline=""
#             ) as csvfile:
#                 writer = csv.writer(csvfile)
#                 writer.writerow([f"{counter}", f"{device.name}", used, total, percentage, category])
#         except:
#             logger.error("gagal dengan function utama iosxe")

#             # Convert the device to Netmiko format
#             netmiko_device = convert_to_netmiko(device)

#             # Establish the Netmiko connection
#             logger.info("Establishing Netmiko connection...")
#             connection = ConnectHandler(**netmiko_device)
#             logger.info("Connection established successfully.")

#             # Send a command and retrieve the output
#             command = "show processes memory"
#             output = connection.send_command(command)

#             with open('lib/getMemmory/ios_xe_switch.template') as template:
#                 template = textfsm.TextFSM(template)

#             # Parse the command output using the template
#             parsed_output = template.ParseText(output)

#             logger.info(parsed_output)

#             header = template.header
#             used_index = header.index('used')
#             total_index = header.index('total')
#             free_index = header.index('free')

#             # Extract the values from the parsed output
#             used = round(int(parsed_output[0][used_index])/1024, 2)
#             total = round(int(parsed_output[0][total_index])/1024, 2)
#             free = round(int(parsed_output[0][free_index])/1024 , 2)
#             percentage = round(used / total * 100, 2)

#             # print(percentage)

#             # Print the extracted values
#             # print(f"Used memory: {used}")
#             # print(f"Total memory: {total}")
#             # print(f"Free memory: {free}")

#             if percentage <= 40:
#                 category = "low"
#             elif percentage <= 70:
#                 category = "medium"
#             elif percentage <= 85:
#                 category = "high"
#             else:
#                 category = "critical"
#             # print(category)

#             result["success"] = True
            
#             with open(
#                         f"out/Capture_Memmory_Utilization/Memmory_{timestamp}.csv", "a", newline=""
#                     ) as csvfile:
#                         writer = csv.writer(csvfile)
#                         writer.writerow([f"{counter}", f"{device.name}", used, total, percentage, category])       
#         return result
#     except Exception as e:
#         logger.error(f"Error connecting to device {device.name}: {e}")
#         result["error"] = str(conn_error)
#         return result

# def get_iosxr_memory_info(device, counter):
#     try:
#         # Connect to the device
#         attempt = 1
#         retry = 0
#         mx_retry = 3
#         while retry < mx_retry:
#             try:
#                 logger.info(f"Connecting to Device: {device.name}")
#                 device.connect(learn_hostname = True, learn_os = True, log_stdout=False,mit=True)
#                 logger.info(f"Successfully Connected to Device: {device.name}")
#                 break
#             except Exception as conn_error:
#                     retry += 1
#                     attempt +=1
#                     if retry < mx_retry:
#                         logger.error(f"Connection attempt {retry}/{mx_retry} failed for {device.name} ({device.connections.cli.ip}): {conn_error}")
#                         logger.info(f"Retrying in 1 seconds...")
#                         time.sleep(2)
#                     else:
#                         logger.error(f"Failed to establish connection to {device.name} ({device.connections.cli.ip}) after {mx_retry} attempts.")
#                         break  # Exit the loop after max retries

#         output = device.parse("show watchdog memory-state")

#         physical_memory_mb = output["node"]["node0_RP0_CPU0"]["physical_memory_mb"]
#         free_memory_mb = output["node"]["node0_RP0_CPU0"]["free_memory_mb"]
#         used_memory_mb = physical_memory_mb - free_memory_mb
#         percentage = round(used_memory_mb / physical_memory_mb * 100, 2)

#         # Categorize percentage based on certain ranges
#         if percentage <= 40:
#             category = "low"
#         elif percentage <= 70:
#             category = "medium"
#         elif percentage <= 85:
#             category = "high"
#         else:
#             category = "critical"

#         # Write the output to the CSV file
#         with open(
#             f"out/Capture_Memmory_Utilization/Memmory_{timestamp}.csv", "a", newline=""
#         ) as csvfile:
#             writer = csv.writer(csvfile)
#             writer.writerow([f"{counter}", f"{device.name}", used_memory_mb, physical_memory_mb, percentage, category])

#         return counter

#     except Exception as e:
#         logger.error(f"Error connecting to device {device.name}: {e}")

# def get_ios_memory_info(device, counter):
#     try:
#         attempt = 1
#         retry = 0
#         mx_retry = 3
#         while retry < mx_retry:
#             try:
#                 logger.info(f"Initiate connection to Device {device.name} attempt {attempt}")
#                 device.connect(mit=True, log_stdout=False)
#                 # Print the output
#                 logger.info(f"Device: {device.name} Connected Successfully")
#                 #send command
#                 try:
#                     output = device.parse("show processes memory")
#                     logger.info(f"Parse Device: {device.name} Data Successfully")
#                 except:
#                     logger.info(f"Failed to Parse Device: {device.name}")
#                 break  # Exit the loop if connected successfully
#             except Exception as conn_error:
#                 retry += 1
#                 attempt +=1
#                 if retry < mx_retry:
#                     logger.error(f"Connection attempt {retry}/{mx_retry} failed for {device.name} ({device.connections.cli.ip}): {conn_error}")
#                     logger.info(f"Retrying in 2 seconds...")
#                     time.sleep(2)
#                 else:
#                     logger.error(f"Failed to establish connection to {device.name} ({device.connections.cli.ip}) after {mx_retry} attempts.")
#                     break  # Exit the loop after max retries

#         used = round(output['processor_pool']['used']/1024/1000, 2)
#         total = round(output['processor_pool']['total']/1024/1000, 2)
#         percentage = round(used / total * 100, 2)

#         # Categorize percentage based on certain ranges
#         if percentage <= 40:
#             category = "low"
#         elif percentage <= 70:
#             category = "medium"
#         elif percentage <= 85:
#             category = "high"
#         else:
#             category = "critical"

#         # Write the output to the CSV file
#         with open(
#             f"out/Capture_Memmory_Utilization/Memmory_{timestamp}.csv", "a", newline=""
#         ) as csvfile:
#             writer = csv.writer(csvfile)
#             writer.writerow([f"{counter}", f"{device.name}", used, total, percentage, category])

#         return counter

#     except Exception as e:
#         logger.error(f"Error connecting to device {device.name}: {e}")

# def get_nxos_memory_info(device, counter):
#     try:
#         try:
#             # Connect to the device
#             attempt = 1
#             retry = 0
#             mx_retry = 3
#             while retry < mx_retry:
#                 try:
#                     logger.info(f"Connecting to Device: {device.name}")
#                     device.connect(learn_hostname = True, learn_os = True, log_stdout=False,mit=True)
#                     logger.info(f"Successfully Connected to Device: {device.name}")
#                     break
#                 except Exception as conn_error:
#                         retry += 1
#                         attempt +=1
#                         if retry < mx_retry:
#                             logger.error(f"Connection attempt {retry}/{mx_retry} failed for {device.name} ({device.connections.cli.ip}): {conn_error}")
#                             logger.info(f"Retrying in 1 seconds...")
#                             time.sleep(2)
#                         else:
#                             logger.error(f"Failed to establish connection to {device.name} ({device.connections.cli.ip}) after {mx_retry} attempts.")
#                             break  # Exit the loop after max retries

#             output = device.parse("show system resources")

#             used = round(output["memory_usage"]["memory_usage_used_kb"]/1024, 2)
#             total = round(output["memory_usage"]["memory_usage_total_kb"]/1024, 2)
#             percentage = round(used / total * 100, 2)

#             # Categorize percentage based on certain ranges
#             if percentage <= 40:
#                 category = "low"
#             elif percentage <= 70:
#                 category = "medium"
#             elif percentage <= 85:
#                 category = "high"
#             else:
#                 category = "critical"

#             # Write the output to the CSV file
#             with open(
#                 f"out/Capture_Memmory_Utilization/Memmory_{timestamp}.csv", "a", newline=""
#             ) as csvfile:
#                 writer = csv.writer(csvfile)
#                 writer.writerow([f"{counter}", f"{device.name}", used, total, percentage, category])

#             return counter
#         except:
#             logger.info("gagal dengan function utama nxos")
#             # Convert the device to Netmiko format
#             netmiko_device = convert_to_netmiko(device)
  
#             # Establish the Netmiko connection
#             logger.info("Establishing Netmiko connection...")
#             connection = ConnectHandler(**netmiko_device)
#             logger.info("Connection established successfully.")

#             # Send a command and retrieve the output
#             command = "show system resources"
#             output = connection.send_command(command)
#             print(output)

#             with open('lib/getMemmory/nxos.template') as template:
#                 template = textfsm.TextFSM(template)

#             # Parse the command output using the template
#             parsed_output = template.ParseText(output)

#             logger.info(parsed_output)

#             header = template.header
#             used_index = header.index('used')
#             total_index = header.index('total')
#             free_index = header.index('free')

#             # Extract the values from the parsed output
#             used = round(int(parsed_output[0][used_index])/1024, 2)
#             total = round(int(parsed_output[0][total_index])/1024, 2)
#             free = round(int(parsed_output[0][free_index])/1024 , 2)
#             percentage = round(used / total * 100, 2)

#             # print(percentage)

#             # Print the extracted values
#             print(f"Used memory: {used}")
#             print(f"Total memory: {total}")
#             print(f"Free memory: {free}")

#             if percentage <= 40:
#                 category = "low"
#             elif percentage <= 70:
#                 category = "medium"
#             elif percentage <= 85:
#                 category = "high"
#             else:
#                 category = "critical"
#             print(category)
    
#             with open(
#                         f"out/Capture_Memmory_Utilization/Memmory_{timestamp}.csv", "a", newline=""
#                     ) as csvfile:
#                         writer = csv.writer(csvfile)
#                         writer.writerow([f"{counter}", f"{device.name}", used, total, percentage, category])       
#         return counter
#     except Exception as e:
#         logger.error(f"Error connecting to device {device.name}: {e}")


def getMemmoryUtils(testbedFile):
    testbed = load(testbedFile)
    results = []
    memmory_list = []

    with concurrent.futures.ThreadPoolExecutor() as executor:    
        futures = [executor.submit(getMemmoryInfo, device) for device in testbed]
        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result()
                results.append(result)                       
                if result["success"]:
                    # print(result)
                    memmory_list.append({"Hostname": result["device"], "data": result["data"]})
                else:
                    logger.error(f"Error with device {result['device']}: {result['message']}, Error: {result['error']}")
            except Exception as exc:
                error_message = f"Exception occurred: {str(exc)}"
                logger.error(error_message)
                results.append({"device": "Unknown", "success": False, "error": str(exc)})
    
    
    memmory_list.sort(key=lambda x: x['Hostname'])
    waktu = datetime.now().strftime("%d-%m-%y_%H_%M_%S")
    csv_filename = f"Memmory_{waktu}.csv"
    csv_filepath = os.path.join("out", "Capture_Memmory_Utilization", csv_filename)
    
    with open(csv_filepath, mode='w', newline='') as csvfile:
        fieldnames = ["No", "Device", "Memory Used in MB", "Memory Total in MB", "Percentage", "Category"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        hostname_counter = 1
        for item in memmory_list:
            # logger.info(item["data"])
            hostname = item["Hostname"]
            data = item["data"]

            for memmory in data:
                row = {
                    'No': hostname_counter,
                    'Device': hostname,
                    'Memory Used in MB': memmory['Usage'],
                    'Memory Total in MB' : memmory['Total'],
                    'Percentage': memmory['Percentage'],
                    'Category': memmory['Category']
                }
                writer.writerow(row)
            hostname_counter += 1
    
    logger.info("Get Memmory Utilization - execution completed successfully.")
    return results
    # logger.info(f"Total Executed Get Memory Device is IOS_XE:{ios_xe_device} IOS_XR:{ios_xr_device} IOS:{ios_device} NXOS:{nxos_device} and Total Device is {total_device}")