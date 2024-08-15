import subprocess

# Run the command
process = subprocess.Popen(
    ['/bin/bash', './lib/createTestbed.sh'],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)

# Capture the output and error
stdout, stderr = process.communicate()

# Print the output and error
print("Standard Output:")
print(stdout.decode())

print("Standard Error:")
print(stderr.decode())

# Check if the process exited successfully
if process.returncode == 0:
    print("Script executed successfully.")
else:
    print(f"Script failed with return code {process.returncode}.")
