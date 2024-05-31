from flask import Flask, render_template,flash,get_flashed_messages,send_file, request,jsonify
from markupsafe import Markup 
from jinja2 import ChoiceLoader, FileSystemLoader
import os,yaml,pytz
from datetime import datetime
from lib.createTestbed import createTestbed
from lib.createInterfaceCRClist import createInterfaceCRCList
from lib.getConfig.main import captureConfig
from lib.getInven.main import getInventMain
from lib.getMemmory.main import getMemmoryUtils
from lib.getCPU.main import getCPUmain
from lib.getCDP.main import getCDPmain
from lib.getCustom.main import getCustomMain
from lib.getCRC.main import interfaceCRC
from lib.getCRC_InterfaceList.main import main_InterfaceCRC
from time import sleep
from lib.logSummary.main import summary_log


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

@app.route('/deviceList', methods=['GET'])
def deviceList():
    if checkTestbedFile()==True:
        # Read YAML file
        with open('testbed/device.yaml', 'r') as file:
            data = yaml.safe_load(file)

        file_path = 'testbed/device.yaml' 
        timestamp = os.path.getmtime(file_path)

        timestamp_dt = datetime.fromtimestamp(timestamp)

        # Set the timezone to GMT-7
        timezone = pytz.timezone('Etc/GMT-7')
        timestamp_dt = timestamp_dt.astimezone(timezone)

        last_modified = timestamp_dt.strftime("%Y-%m-%d %H:%M:%S")
    else:
        data = False
        
        last_modified = ""
    
    return render_template('deviceList.html',dataDevices=data,config=last_modified)

@app.route('/interfaceListed', methods=['GET'])
def interfaceListed():
    if checkTestbedFile()==True:
        # Read YAML file
        try:
            with open('testbed/interfaceCRClist.yaml', 'r') as file:
                data = yaml.safe_load(file)
        except Exception as e:
            data = False
            last_modified = "File Interface CRC list not found"
            return render_template('interfaceListed.html',dataDevices=data,config=last_modified)

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
        
    return render_template('interfaceListed.html',dataDevices=data,config=last_modified)    

@app.route('/uploadCSV', methods=['POST'])
def uploadCSV():
    file = request.files['file']
    
    if file:
        # Access file information
        filename = file.filename
        file.save('assets/import/' + filename)

        if createTestbed(filename) == True:
            return 'success create testbed file'
        else:
            return 'Error while creating testbed file'
    return 'No file uploaded'

@app.route('/uploadInterfaceCRCfile', methods=['POST'])
def uploadInterfaceCRCfile():
    file = request.files['file']
    
    if file:
        # Access file information
        filename = file.filename
        file.save('assets/import/' + filename)

        if createInterfaceCRCList(filename) == True:
            return 'success create testbed interface CRC list file'
        else:
            return 'Error while creating testbed interface CRC list file'
    return 'No file uploaded'

@app.route('/getConfig', methods=['POST'])
def getConfig():
        if checkTestbedFile()==True:
            waktu = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            result = captureConfig(testbedFile)
            flash(result)
            flash("Logs details : "+summary_log(waktu))
            return jsonify(data=get_flashed_messages())
        else:
            flash(f"device list file is not ready, please check the device list file",'error')
            return jsonify(data=get_flashed_messages())  

@app.route('/getInvent', methods=['POST'])
def getInvent():
    if checkTestbedFile()==True:
        getInventMain()
        flash(f"Success to get Memmory Utilization devices")
        return jsonify(data=get_flashed_messages())
    else:
        flash(f"device list file is not ready, please check the device list file")
        return jsonify(data=get_flashed_messages())

@app.route('/getMemUtils', methods=['POST'])
def getMemUtils():
    if checkTestbedFile()==True:
        getMemmoryUtils(testbedFile)
        flash(f"Success to get Memmory devices")
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
        # waktu = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        result = interfaceCRC(testbedFile)
        flash(result)
        # flash("Logs details : "+summary_log(waktu))
        return jsonify(data=get_flashed_messages())
    else:
        flash(f"device list file is not ready, please check the device list file")
        return jsonify(data=get_flashed_messages())
    
@app.route('/getCRClisted', methods=['POST'])
def getCRClisted():
    if checkTestbedFile()==True:
        # waktu = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        result = main_InterfaceCRC(crcListedFile)
        flash(result)
        # flash("Logs details : "+summary_log(waktu))
        return jsonify(data=get_flashed_messages())
    else:
        flash(f"device list file is not ready, please check the device list file")

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
        print(data['name'])

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
    print(data['file'])
    file_path = './out/'+data['folder']+'/'+data['file']
    print(file_path)

    # Send the file as a response
    return send_file(file_path, as_attachment=True)


app.run(host="0.0.0.0",debug=True,port=8081)