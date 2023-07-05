from flask import Flask, render_template,flash,get_flashed_messages,send_file, request,jsonify
from markupsafe import Markup 
from jinja2 import ChoiceLoader, FileSystemLoader
import os,yaml,pytz
from datetime import datetime
from lib.createTestbed import createTestbed
from lib.getConfig.main import captureConfigX
from time import sleep


from genie.testbed import load
import concurrent.futures

template_folder=["assets/views/","testbed/",'lib/','assets/import/']

template_loader = ChoiceLoader([
    FileSystemLoader(folder) for folder in template_folder
])

app = Flask(__name__,static_folder="assets/")

app.jinja_loader = template_loader

testbedFile = 'testbed/device.yaml'

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

@app.route('/getConfig', methods=['POST'])
def getConfig():
    if checkTestbedFile()==True:
        
        def captureConfigX(device):
            # Load the testbed file
            # Send a command to the device
            try:
                device.connect(log_stdout=False)
                #Print the output
                hostname = device.name
                #   logger.info('---getting capture config from device '+hostname+'---')
                waktu = datetime.now().strftime("%d-%m-%y_%H_%M_%S")
                NameFile = hostname + "_" + waktu +".txt"
                file_path = "out/CaptureConfig/"
                output = device.execute('show running-config')
                file_name = os.path.join(file_path,NameFile)
                # flash(f"Succes get config {device.name}")
                try:
                    with open(file_name, 'a') as file:
                        file.write(f'''{output}''')
                except  Exception as e:
                    return f"Error write to file for device {device.name}: {e}"
            except Exception as e:
            #print(f"Error connecting to device {device.name}: {e}")
                return f"Error connecting to device {device.name}: {e}"
            return f"Succes get config {device.name}"

        testbed = load(testbedFile)
        # Create a list of futures for iosxe and iosxr devices
        futures = []
        with concurrent.futures.ThreadPoolExecutor() as executor:
            for device in testbed:
                futures.append(executor.submit(captureConfigX, device))
                # flash(f"Connecting to device {device.name}",'info')
                sleep(0.1)
            # Wait for all futures to complete

        for future in concurrent.futures.as_completed(futures):
            try:
                flash(future.result())
            except Exception as exc:
                flash(f"{exc} occurred while processing device {device.name}")
        # flash("Get Config -  execution completed successfully.",'info')
        return jsonify(data=get_flashed_messages())

@app.route('/getInvent', methods=['POST'])
def getInvent():
    data = "Getting Inventory devices"
    return data

@app.route('/getMemUtils', methods=['POST'])
def getMemUtils():
    data = "Getting Memmory Utilization devices"
    return data

@app.route('/getCPUUtils', methods=['POST'])
def getCPUUtils():
    data = "Getting CPU Utilization devices"
    return data

@app.route('/customPage', methods=['GET'])
def customPage():
    return render_template("customCommand.html") 

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

    file_path = './out/'+data['folder']+'/'+data['file']
    print(file_path)

    # Send the file as a response
    return send_file(file_path, as_attachment=True)


app.run(debug=True,port=8081)