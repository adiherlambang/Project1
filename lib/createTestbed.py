import subprocess

def createTestbed(input_file):
    # Start Bash script as subprocess with input from variable
    result = subprocess.Popen(['/bin/bash', './lib/createTestbed.sh'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

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