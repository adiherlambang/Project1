from lib.getCustom.device import Routers, TIMESTAMP, ERROR_COMMAND
import csv
import threading
import os
import yaml

TITLE = "getCPU"
COMMAND1 = "show processes cpu"
COMMAND2 = "show processes cpu"
HEADERS = ['No', 'Device', 'CPU Used', 'CPU Free', 'Category']
TESTBED =  "testbed/device.yaml"
TEMPLATE_NUMBERS = 4
devices = []
success_counter = []
fail_counter = []

def getCPUmain():
    read_testbed()
    export_headers()
    i = 1
    threads = []
    for device in devices:
        t = threading.Thread(target=process_device, args=(device, i))
        t.start()
        threads.append(t)
        i += 1

    for t in threads:
        t.join()

    end_summary()

def process_device(device, i):
    parsed = ""
    num_try = 0
    device.command_template = 'CPU_Utils'
    device.out_path = f"out/{TITLE}/"
    device.log_path = f"log/{TITLE}.log"
    device.errorlog = f"log/error/{TITLE}-error.log"
    device.create_folder()
    if device.connect(i):
        command = COMMAND1
        output = "Function exception"
        while output == "Function exception" and device.exception_counter < 3:
            output = device.connect_command(command)

        #try other command
        if [c for c in ERROR_COMMAND if c in output]:
            device.logging_error(f"{device.hostname} : Command [{command}] Failed, trying [{COMMAND2}]")
            command = COMMAND2
            output = device.connect_command(command)
        
        #final check output
        if [c for c in ERROR_COMMAND if c in output]:
            device.logging_error(f"{device.hostname} : Output return empty for command [{command}]")
        else:
            while parsed == "" and num_try < TEMPLATE_NUMBERS:
                num_try += 1
                parsed = device.parse(COMMAND1, output, num_try)
        
        #special templates
        if parsed != "":
            if num_try == 3:
                final = export_csv_3(parsed, i, device.hostname)
                device.export_data(final)
            else:
                final = export_csv(parsed, i, device.hostname)
                device.export_data(final)

            success_counter.append(0)
        else:
            device.logging_error(f"{device.hostname} : Parsing failed after [{num_try}] tries.")
            fail_counter.append(f'{device.ip} - {device.ios_os} - {device.hostname}')

        device.disconnect()
    else:
        fail_counter.append(f'{device.ip} - {device.ios_os} - {device.hostname}')

def export_headers():
    outpath = f'out/{TITLE}/'
    if not os.path.exists(outpath):
        os.makedirs(outpath)

    with open(f"{outpath}CPU_Utils_{TIMESTAMP}.csv", 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(HEADERS)

def read_testbed():
    with open(TESTBED) as f:
        device = yaml.safe_load(f)['devices']
        for d in device:
            the_ip = device[d]['connections']['cli']['ip']
            the_protocol = device[d]['connections']['cli']['protocol']
            the_username = device[d]['credentials']['default']['username']
            the_password = device[d]['credentials']['default']['password']
            the_enable = device[d]['credentials']['enable']['password']
            the_ios_os = device[d]['os']

            new_device = Routers(
                d,
                the_ip,
                the_username,
                the_password,
                the_enable,
                the_ios_os,
                the_protocol
            )
            devices.append(new_device)


def end_summary():
    print(f'\n=> Success : [{len(success_counter)}/{len(devices)}]\n')
    if len(fail_counter) > 0:
        print(f'=> Failed  :')
        for idx, fc in enumerate(fail_counter):
            print(f'   {idx+1}. {fc}')
        print('')
        
#universal template
def export_csv(parsed, i, hostname):
    cpu_load = 0
    for p in parsed:
        cpu_load = int(p['cpu_5_min'])
        if cpu_load <= 40:
            category = 'LOW'
        elif cpu_load <= 70:
            category = 'MEDIUM'
        elif cpu_load <= 85:
            category = 'HIGH'
        else:
            category = 'CRITICAL'

    free_load = str(100 - cpu_load) + '%'
    cpu_load = str(cpu_load) + '%'
    
    final = [i, hostname, cpu_load, free_load, category]
    return final

#template no 3
def export_csv_3(parsed, i, hostname):
    cpu_load = 0
    for p in parsed:
        cpu_load = float(p['user']) + float(p['kernel'])
        free_load = float(p['user'])

    if cpu_load <= 40:
        category = 'LOW'
    elif cpu_load <= 70:
        category = 'MEDIUM'
    elif cpu_load <= 85:
        category = 'HIGH'
    else:
        category = 'CRITICAL'

    free_load = p['user']+'%'
    cpu_load = str(round(cpu_load,2)) + '%'
    
    final = [i, hostname, cpu_load, free_load, category]
    return final