from flask import Flask, render_template, url_for
import flask, os, sys, inspect, shutil, time, datetime, gpiozero, subprocess, re
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
import graph, tempreport

while str(os.path.isfile(parDir + '/data/config.csv')) == 'False':
  time.sleep(1)

readme = parDir + '/README.md'
tempWebVer = tempreport.readLine(readme, 'keyword', 'Temp-web', char = ': ')
tempVer = tempreport.readLine(readme, 'keyword', 'Temp-report', char = ': ')

shutil.copy2(parDir + '/temps.log', currDir + '/temps.log')
graphPointCount = tempreport.readCSVLine(parDir + '/data/config.csv', 2, 'keyword', 'graph_point_count', var_type = 'int')
graph.generateGraph(graphPointCount)
shutil.move(currDir + '/temps.log', currDir + '/static/temps.log')
shutil.move(currDir + '/graph.png', currDir + '/static/graph.png')

@app.route('/')
def main(flaskVer=flask.__version__, tempWebVer=tempWebVer, tempVer=tempVer, pointCount=graphPointCount, cpu=cpu):
    def measureTemp(mode):
        if mode == 'temp':
            value = str(tempreport.measureTemp()) + '°C'
            print('Updated Temperature')
        elif mode == 'time':
            value = datetime.datetime.now().strftime("%H:%M:%S")
            print('Updated Time')
        return value

    def maxTemp(mode):
        if mode == 'temp':
            value = str(tempreport.readCSVLine(parDir + '/data/temp-records.csv', 2, 'keyword', 'max', val_type = 'str')) + '°C'
            print('Updated Max Temperature')
        elif mode == 'time':
            value = tempreport.readCSVLine(parDir + '/data/temp-records.csv', 3, 'keyword', 'max', val_type = 'str')
            print('Updated Max Temperature Time')
        return value

    def minTemp(mode):
        if mode == 'temp':
            value = str(tempreport.readCSVLine(parDir + '/data/temp-records.csv', 2, 'keyword', 'min', val_type = 'str')) + '°C'
            print('Updated Max Temperature')
        elif mode == 'time':
            value = tempreport.readCSVLine(parDir + '/data/temp-records.csv', 3, 'keyword', 'min', val_type = 'str')
            print('Updated Max Temperature Time')
        return value

    shutil.copy2(parDir + '/temps.log', currDir + '/temps.log')
    graphPointCount = tempreport.readCSVLine(parDir + '/data/config.csv', 2, 'keyword', 'graph_point_count', var_type = 'int')
    graph.generateGraph(graphPointCount)
    shutil.move(currDir + '/temps.log', currDir + '/static/temps.log')
    shutil.move(currDir + '/graph.png', currDir + '/static/graph.png')
    print('Updated Files')

    with open(currDir + '/static/temps.log', "r") as f:
        logContent = f.read()
        logContent = logContent.rsplit('\n', 1)
        logContent = ''.join(logContent)

    with open(currDir + '/static/temps.log', "r") as f:
        lineCount = len(f.readlines())
        print('Found ' + str(lineCount) + ' lines')
    try:
        tempVerRaw = tempVer[:-2]
        latestTempVer = subprocess.check_output(["bash", "version.sh"])
        latestTempVer = re.findall('\d+.\d+', str(latestTempVer))[0]

        if latestTempVer > tempVerRaw:
            outdated = 'True'
            print('Program outdated')
        else:
            outdated = 'False'
    except:
        outdated = 'False'

    return render_template('tempreport.html', flaskVer=flaskVer, tempWebVer=tempWebVer, tempVer=tempVer, measureTemp=measureTemp, maxTemp=maxTemp, minTemp=minTemp, logContent=logContent, lineCount=lineCount, pointCount=pointCount, cpuTemp=str(cpu.temperature) + '°C', outdated=outdated)

if __name__ == "__main__":
    app.run(host= '0.0.0.0', port= 80)
