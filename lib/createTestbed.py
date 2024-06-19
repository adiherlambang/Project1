import subprocess
import os

testbed_log = './log/testbedCreate.log'

testbed_log_dir = os.path.dirname(testbed_log)

if not os.path.exists(testbed_log_dir):
    with open(testbed_log_dir, 'w') as file:
        file.write('')  # Create an empty log file
    print(f"Log file {testbed_log_dir} created.")  

def createTestbed(input_file):
    with open(testbed_log, 'a') as out:
        result = subprocess.Popen(['/bin/bash', './lib/createTestbed.sh'], stdin=subprocess.PIPE, stdout=out, stderr=out)

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