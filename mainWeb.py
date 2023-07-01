from flask import Flask, render_template, request,jsonify

app = Flask(__name__,template_folder="assets/views/",static_folder="assets/")

@app.route('/')
def app_home():
    return render_template("index.html")

@app.route('/deviceList')
def deviceList():
    return render_template("deviceList.html")

@app.route('/getConfig', methods=['POST'])
def getConfig():
    data = "Getting Config devices"
    return data

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

app.run(debug=True,port=8081)