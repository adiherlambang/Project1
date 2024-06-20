from flask import Flask, render_template,flash,get_flashed_messages,send_file, request,jsonify
from markupsafe import Markup 
from jinja2 import ChoiceLoader, FileSystemLoader
import os,yaml,pytz
from datetime import datetime
from lib.createTestbed import createTestbed
from lib.createInterfaceCRClist import createInterfaceCRCList
from lib.getConfig.main import captureConfig
from lib.getInven.main import captureInventory
from lib.getMemmory.main import getMemmoryUtils
from lib.getCPU.main import getCPUmain
from lib.getCDP.main import getCDPmain
from lib.getCustom.main import getCustomMain
from lib.getCRC.main import interfaceCRC
from lib.getCRC_InterfaceList.main import main_InterfaceCRC
from time import sleep
from lib.logSummary.main import summary_log
import logging
from rich.logging import RichHandler
from genie.testbed import load
import concurrent.futures

template_folder=["assets/views/","testbed/",'lib/','assets/import/']

template_loader = ChoiceLoader([
    FileSystemLoader(folder) for folder in template_folder
])

app = Flask(__name__,static_folder="assets/")

app.jinja_loader = template_loader

testbedFile = 'testbed/device.yaml'
crcListedFile = 'testbed/interfaceCRClist.yaml'

app.secret_key = 'myApps'

waktu = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

log_file_path = 'log/service_api.log'

log_dir = os.path.dirname(log_file_path)
if not os.path.exists(log_dir):
    os.makedirs(log_dir)
        
if not os.path.exists(log_file_path):
    with open(log_file_path, 'w') as file:
        file.write('')  # Create an empty log file   
        
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
# the handler determines where the logs go: stdout/file
shell_handler = RichHandler()
file_handler = logging.FileHandler(log_file_path)
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

logger.info("Web service ProjectOne is Running")

def checkTestbedFile():
    if os.path.exists(testbedFile):
        return True
    else:
        return False

# @app.after_request
# def add_headers(response):
#     # Disable caching
#     response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
#     response.headers['Pragma'] = 'no-cache'
#     response.headers['Expires'] = '-1'
#     return response

@app.route('/')
def app_home():
    if not os.path.exists("testbed/device.yaml"):
        data = Markup('''<span><i id="checker" class="fas fa-xmark-circle" data-toggle="tooltip" data-placement="right" title="Testbedfile is not READY" style="color: red;"></i></span>''')
    else:
        data= Markup('''<span><i id="checker" class="fas fa-check-circle" data-toggle="tooltip" data-placement="right" title="Testbedfile is READY" style="color: green;"></i></span>''')

    return render_template("index.html",data = data)


@app.route('/deviceListData', methods=['GET'])
def get_data():
    if checkTestbedFile()==True:
        with open('testbed/device.yaml', 'r') as file:
            data = yaml.safe_load(file)

        devices = data['devices']
        
        data = [
            {
                'name': name,
                'ip': device['connections']['cli']['ip'],
                'protocol': device['connections']['cli']['protocol'],
                'username': device['credentials']['default']['username'],
                'password': device['credentials']['default']['password'],
                'os': device['os'],
                'type': device['type']
            }
            for name, device in devices.items()
        ]
        
        draw = request.args.get('draw')
        start = int(request.args.get('start', 0))
        length = int(request.args.get('length', 10))
        search_value = request.args.get('search[value]', '').lower()

        filtered_data = [item for item in data if search_value in item['name'].lower()]

        paginated_data = filtered_data[start:start + length]
        
        response = {
            'draw': draw,
            'recordsTotal': len(data),
            'recordsFiltered': len(filtered_data),
            'data': paginated_data
        }
        
        return jsonify(response)
        
        

@app.route('/deviceList', methods=['GET'])
def deviceList():
    if checkTestbedFile()==True:
        file_path = 'testbed/device.yaml'
        timestamp = os.path.getmtime(file_path)

        timestamp_dt = datetime.fromtimestamp(timestamp)

        # Set the timezone to GMT-7
        timezone = pytz.timezone('Etc/GMT-7')
        timestamp_dt = timestamp_dt.astimezone(timezone)

        last_modified = timestamp_dt.strftime("%Y-%m-%d %H:%M:%S")
    else:
        last_modified = ""
        
    return render_template('deviceList_new.html',config=last_modified)

@app.route('/interfaceListed', methods=['GET'])
def interfaceListed():
    if checkTestbedFile()==True:
        file_path = 'testbed/interfaceCRClist.yaml' 
        timestamp = os.path.getmtime(file_path)

        timestamp_dt = datetime.fromtimestamp(timestamp)

        # Set the timezone to GMT-7
        timezone = pytz.timezone('Etc/GMT-7')
        timestamp_dt = timestamp_dt.astimezone(timezone)

        last_modified = timestamp_dt.strftime("%Y-%m-%d %H:%M:%S")
    else:
        data = False
        
        last_modified = ""
        
    return render_template('interfaceListed_new.html',config=last_modified)    

@app.route('/interfaceListData', methods=['GET'])
def interfaceListData():
    if checkTestbedFile()==True:
        with open('testbed/interfaceCRClist.yaml', 'r') as file:
            yaml_data = yaml.safe_load(file)

        devices = yaml_data['devices']
        topology = yaml_data['topology']
        
        data = []
        for name, device in devices.items():
            device_info = {
                'name': name,
                'ip': device['connections']['cli']['ip'],
                'protocol': device['connections']['cli']['protocol'],
                'username': device['credentials']['default']['username'],
                'password': device['credentials']['default']['password'],
                'os': device['os'],
                'type': device['type'],
                'interfaces':[]
            }

            # Extract topology information if available
            if name in topology:
                interfaces = topology[name]['interfaces']
                for intf_name, intf_data in interfaces.items():
                    intf_info = f"{intf_name}"
                    device_info['interfaces'].append(intf_info)

            # Combine interface information into a single string
            device_info['interfaces'] = ', '.join(device_info['interfaces'])
            data.append(device_info)

        
        draw = request.args.get('draw')
        start = int(request.args.get('start', 0))
        length = int(request.args.get('length', 10))
        search_value = request.args.get('search[value]', '').lower()

        filtered_data = [item for item in data if search_value in item['name'].lower()]

        paginated_data = filtered_data[start:start + length]
        
        response = {
            'draw': draw,
            'recordsTotal': len(data),
            'recordsFiltered': len(filtered_data),
            'data': paginated_data
        }
        
        return jsonify(response)

@app.route('/uploadCSV', methods=['POST'])
def uploadCSV():
    file = request.files['file']
    if file:
        # Access file information
        filename = file.filename
        file.save('./assets/import/' + filename)
        generateTestbed = createTestbed(filename)
        logger.info(generateTestbed)
        return generateTestbed
    return 'No file uploaded'

@app.route('/uploadInterfaceCRCfile', methods=['POST'])
def uploadInterfaceCRCfile():
    file = request.files['file']
    
    if file:
        # Access file information
        filename = file.filename
        file.save('assets/import/' + filename)
        generateTestbed = createInterfaceCRCList(filename)
        logger.info(generateTestbed)
        return generateTestbed
    return 'No file uploaded'

@app.route('/getConfig', methods=['POST'])
def getConfig():
    if checkTestbedFile():
        results = captureConfig(testbedFile)
        error_count=0
        success_count=0
        for result in results:
            if result["success"]:
                # flash(f"Success: {result['message']}")
                success_count +=1
            else:
                # flash(f"Error: {result['message']} - {result['error']}", 'error')
                error_count +=1
                
        flash(f"Finish Capture Config Data, Success :{success_count} Error :{error_count} from {len(results)} device in the list")    
        flash("Logs details : " + summary_log(waktu,'CaptureConfig'))
        return jsonify(data=get_flashed_messages())
    else:
        flash(f"Device list file is not ready, please check the device list file", 'error')
        return jsonify(data=get_flashed_messages())

@app.route('/getInvent', methods=['POST'])
def getInvent():
    if checkTestbedFile():
        results = captureInventory(testbedFile)
        error_count = 0
        success_count = 0
        
        for result in results:
            if result["success"]:
                # flash(f"Success: {result['message']}")
                success_count += 1
            else:
                # flash(f"Error: {result['message']} - {result['error']}", 'error')
                error_count += 1
        
        flash(f"Finish Capture Inventory Data, Success :{success_count} Error :{error_count} from {len(results)} device in the list")
        flash("Logs details : " + summary_log(waktu,'CaptureInventory'))
        return jsonify(data=get_flashed_messages())
    else:
        flash(f"Device list file is not ready, please check the device list file", 'error')
        return jsonify(data=get_flashed_messages())

@app.route('/getMemUtils', methods=['POST'])
def getMemUtils():
    if checkTestbedFile()==True:
        results = getMemmoryUtils(testbedFile)
        error_count = 0
        success_count = 0
        
        for result in results:
            if result["success"]:
                # flash(f"Success: {result['message']}")
                success_count += 1
            else:
                # flash(f"Error: {result['message']} - {result['error']}", 'error')
                error_count += 1
        
        flash(f"Finish Capture Memmory Utilization Data, Success :{success_count} Error :{error_count} from {len(results)} device in the list")
        flash("Logs details : " + summary_log(waktu,'getMemmoryUtils'))
        return jsonify(data=get_flashed_messages())
    else:
        flash(f"device list file is not ready, please check the device list file")
        return jsonify(data=get_flashed_messages())

@app.route('/getCPUUtils', methods=['POST'])
def getCPUUtils():
    if checkTestbedFile()==True:
        getCPUmain()
        flash(f"Success to get CPU Utilization devices")
        return jsonify(data=get_flashed_messages())
    else:
        flash(f"device list file is not ready, please check the device list file")
        return jsonify(data=get_flashed_messages())

@app.route('/getCDP', methods=['POST'])
def getCDP():
    if checkTestbedFile()==True:
        getCDPmain()
        flash(f"Success to get CDP Neighbours devices")
        return jsonify(data=get_flashed_messages())
    else:
        flash(f"device list file is not ready, please check the device list file")
        return jsonify(data=get_flashed_messages())

@app.route('/customPage', methods=['POST','GET'])
def customPage():
    if request.method=='POST':
        if checkTestbedFile()==True:
            getCustomMain()
            flash(f"Success to get CDP Neighbours devices")
            return jsonify(data=get_flashed_messages())
        else:
            flash(f"device list file is not ready, please check the device list file")
            return jsonify(data=get_flashed_messages())
    if request.method=='GET':
        return render_template("customCommand.html")   

@app.route('/getCRCAll', methods=['POST'])
def getCRCAll():
    if checkTestbedFile()==True:
        results = interfaceCRC(testbedFile)
        error_count = 0
        success_count = 0
        
        for result in results:
            if result["success"]:
                # flash(f"Success: {result['message']}")
                success_count += 1
            else:
                # flash(f"Error: {result['message']} - {result['error']}", 'error')
                error_count += 1
        
        flash(f"Finish Capture Interface CRC Data, Success :{success_count} Error :{error_count} from {len(results)} device in the list")
        flash("Logs details : " + summary_log(waktu,'Interface-CRC'))
        return jsonify(data=get_flashed_messages())
    else:
        flash(f"device list file is not ready, please check the device list file")
        return jsonify(data=get_flashed_messages())
    
@app.route('/getCRClisted', methods=['POST'])
def getCRClisted():
    if checkTestbedFile()==True:
        results = main_InterfaceCRC(crcListedFile)
        error_count = 0
        success_count = 0
        
        for result in results:
            if result["success"]:
                # flash(f"Success: {result['message']}")
                success_count += 1
            else:
                # flash(f"Error: {result['message']} - {result['error']}", 'error')
                error_count += 1
        
        flash(f"Finish Capture Listed Interface CRC Data, Success :{success_count} Error :{error_count} from {len(results)} device in the list")
        flash("Logs details : " + summary_log(waktu,'InterfaceListed-CRC'))
        return jsonify(data=get_flashed_messages())
    else:
        flash(f"device list file is not ready, please check the device list file")
        return jsonify(data=get_flashed_messages())

@app.route('/getOutput', methods=['POST','GET'])
def getOutput():
    if request.method == 'GET':
        directory = './out'  # Specify the directory path

        # Get the directory contents
        contents = os.listdir(directory)

        # Filter out the current directory and parent directory references
        filtered_contents = [item for item in contents if item not in ['.', '..','.DS_Store']]
        # print(filtered_contents)
        return render_template("outputFile.html",contents=filtered_contents)
    if request.method == 'POST':
        data = request.get_json('data')
        logger.info(data['name'])

        directory = './out/'+data['name']
        # Get the directory contents
        contents = os.listdir(directory)

        # Filter out the current directory and parent directory references
        filtered_contents = [item for item in contents if item not in ['.', '..','.DS_Store']]
        # flash(filtered_contents)

        return jsonify(filtered_contents)

@app.route('/downloadFile', methods=['post'])
def downloadFile():
    # Path to the file you want to download
    data = request.get_json('data')
    logger.info(data['file'])
    file_path = './out/'+data['folder']+'/'+data['file']
    logger.info(file_path)

    # Send the file as a response
    return send_file(file_path, as_attachment=True)


if __name__ == "__main__":
    app.run()
