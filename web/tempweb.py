from flask import Flask, render_template, request, url_for
import flask, os, sys, inspect, time, datetime, gpiozero, base64
import PIL.Image
app = Flask(__name__, static_url_path='/static')

try:
    from gpiozero import CPUTemperature
    cpu = CPUTemperature()
except:
    class cpu:
        temperature = 'Error'

currDir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parDir = os.path.dirname(currDir)
sys.path.insert(0,parDir)
import graph
import commonfuncs as tempreport

#Load config
print('Waiting for config...')
while os.path.isfile('../data/config.py') == False:
  time.sleep(1)
sys.path.insert(1, '../data/')
import config
print("Loaded config")

#Recreate symlinks for access to the log for webpage and graph.py
if os.path.isfile(currDir + '/temps.log') == True:
  os.remove(currDir + '/temps.log')
if os.path.isfile(currDir + '/static/temps.log') == True:
  os.remove(currDir + '/static/temps.log')
os.symlink(parDir + '/temps.log', currDir + '/temps.log')
os.symlink(parDir + '/temps.log', currDir + '/static/temps.log')

#Define the main route
@app.route('/', methods = ['POST','GET'])
def main(flaskVer=flask.__version__, pointCount=config.graph_point_count, cpu=cpu, hourPointCount=config.log_interval):
    def measureTemp(mode):
        if mode == 'temp':
            return str(tempreport.measureTemp())
        elif mode == 'time':
            return datetime.datetime.now().strftime("%H:%M:%S")

    def getTemp(maxOrMin, info):
        if info == 'temp':
            targetPosition = 2
        else:
            targetPosition = 3
        return str(tempreport.readCSVLine(parDir + '/data/temp-records.csv', targetPosition, 'keyword', maxOrMin))

    print("\n--------------------\n")

    with open(currDir + '/static/temps.log', "r", encoding='utf-8') as f:
        #Save log contents
        logContent = f.read()
        logContent = logContent.rsplit('\n', 1)
        logContent = ''.join(logContent)

        #Reset file pointer to get number of lines
        f.seek(0)
        lineCount = len(f.readlines())
        print('Found ' + str(lineCount) + ' lines')

    #Use requested number of points, if specified
    if request.method == 'POST':
        result = request.form
        pointCount = result['pointsrequested']

    graphImageData = graph.generateGraph(int(pointCount), config.area_name, export_base64 = True)
    print(f"Drew graph with {pointCount} points")
    print('Updated Files')
    print("\n--------------------\n")
    hourPointCount = int(3600 / hourPointCount)
    cpuTemp = f"{str(cpu.temperature)} °C"
    templateData = {
        "graphImageData": graphImageData,
        "measureTemp": measureTemp,
        "getTemp": getTemp,
        "logContent": logContent,
        "lineCount": lineCount,
        "pointCount": pointCount,
        "hourPointCount": hourPointCount,
        "cpuTemp": cpuTemp,
    }
    return render_template('tempreport.html', **templateData)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
