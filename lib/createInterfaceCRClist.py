import subprocess
import os

crcList_log = './log/createInterfaceCRCList.log'

crcList_log_dir = os.path.dirname(crcList_log)

if not os.path.exists(crcList_log_dir):
    with open(crcList_log_dir, 'w') as file:
        file.write('')  # Create an empty log file
    print(f"Log file {crcList_log_dir} created.")  

def createInterfaceCRCList(input_file):
    with open(crcList_log, 'a') as out:
        result = subprocess.Popen(['/bin/bash', './lib/createInterfaceCRCList.sh'], stdin=subprocess.PIPE, stdout=out, stderr=out)

    # Send input to subprocess and get output and errors
    output, errors = result.communicate(input=input_file.encode())

    # Get return code
    return_code = result.returncode

    if return_code == 0:
        # Success
        print("Importing file..."+input_file)

        print(f"Success: {output.decode().strip()}")
        print("---testbed file ready---")
        return True
    elif return_code == 1:
        # Error
        print(f"Error: {errors.decode().strip()}")
        return False