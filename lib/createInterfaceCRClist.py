import subprocess
import os
import csv
import yaml


crcList_log = './log/createInterfaceCRCList.log'

crcList_log_dir = os.path.dirname(crcList_log)

if not os.path.exists(crcList_log_dir):
    with open(crcList_log_dir, 'w') as file:
        file.write('')  # Create an empty log file
    print(f"Log file {crcList_log_dir} created.")  
    
yaml_file_path = 'testbed/interfaceCRClist.yaml'

def createInterfaceCRCList(input_file):
    csv_file_path = 'assets/import/' + input_file

    msg = {
        'status': False,
        'message': ""
    }
    
    testbed = {
        'devices': {},
        'topology': {}
    }
    try:
        print(f'Processing create testbed file, from input file {csv_file_path}')
        with open(csv_file_path, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                hostname = row['hostname']
                if hostname not in testbed['devices']:
                    testbed['devices'][hostname] = {
                        'os': row['os'],
                        'type': row['os'],
                        'credentials': {
                            'default': {
                                'username': row['username'],
                                'password': row['password']
                            },
                            'enable': {
                                'password': row['enable_password']
                            }
                        },
                        'connections': {
                            'cli': {
                                'protocol': row['protocol'],
                                'ip': row['ip']
                            }
                        }
                    }
                    testbed['topology'][hostname] = {'interfaces': {}}
                
                interface_name = row['interface']
                testbed['topology'][hostname]['interfaces'][interface_name] = {
                    'ipv4': '0.0.0.0/24',  # Adjust as needed if you have IP info
                    'link': '',
                    'type': 'ethernet'
                }


        with open(yaml_file_path, 'w') as file:
            yaml.dump(testbed, file, default_flow_style=False)

        print(f'Testbed YAML file has been created at: {yaml_file_path}')
        msg['status'] = True

        return msg
    except Exception as error_create_testbed:
        print(f"error: {error_create_testbed}")
        msg['message'] = str(error_create_testbed)
        return msg

    # with open(crcList_log, 'a') as out:
    #     result = subprocess.Popen(['/bin/bash', './lib/createInterfaceCRCList.sh'], stdin=subprocess.PIPE, stdout=out, stderr=out)

    # # Send input to subprocess and get output and errors
    # output, errors = result.communicate(input=input_file.encode())

    # # Get return code
    # return_code = result.returncode

    # if return_code == 0:
    #     # Success
    #     print("Importing file..."+input_file)

    #     print(f"Success: {output.decode().strip()}")
    #     print("---testbed file ready---")
    #     return True
    # elif return_code == 1:
    #     # Error
    #     print(f"Error: {errors.decode().strip()}")
    #     return False