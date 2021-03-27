from flask import Flask, render_template, request, url_for
import flask, os, sys, inspect, shutil, time, datetime, gpiozero, subprocess, re, base64
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
import graph, tempreport

#Load config
while os.path.isfile('../data/config.py') == False:
  time.sleep(1)
sys.path.insert(1, '../data/')
import config
print("Loaded config")

#Generate / prepare some website assets
shutil.copy2(parDir + '/temps.log', currDir + '/temps.log')
graph.generateGraph(config.graph_point_count, config.area_name)
shutil.move(currDir + '/temps.log', currDir + '/static/temps.log')
shutil.move(currDir + '/graph.png', currDir + '/static/graph.png')

@app.route('/', methods = ['POST','GET'])
def main(flaskVer=flask.__version__, pointCount=config.graph_point_count, cpu=cpu):
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
            value = str(tempreport.readCSVLine(parDir + '/data/temp-records.csv', 2, 'keyword', 'max')) + '°C'
            print('Updated Max Temperature')
        elif mode == 'time':
            value = str(tempreport.readCSVLine(parDir + '/data/temp-records.csv', 3, 'keyword', 'max'))
            print('Updated Max Temperature Time')
        return value

    def minTemp(mode):
        if mode == 'temp':
            value = str(tempreport.readCSVLine(parDir + '/data/temp-records.csv', 2, 'keyword', 'min')) + '°C'
            print('Updated Max Temperature')
        elif mode == 'time':
            value = str(tempreport.readCSVLine(parDir + '/data/temp-records.csv', 3, 'keyword', 'min'))
            print('Updated Max Temperature Time')
        return value


    with open(currDir + '/static/temps.log', "r", encoding='utf-8') as f:
        logContent = f.read()
        logContent = logContent.rsplit('\n', 1)
        logContent = ''.join(logContent)

    with open(currDir + '/static/temps.log', "r", encoding='utf-8') as f:
        lineCount = len(f.readlines())
        print('Found ' + str(lineCount) + ' lines')

    if request.method == 'POST':
        result = request.form
        pointCount = result['pointsrequested']

    shutil.copy2(parDir + '/temps.log', currDir + '/temps.log')
    graph.generateGraph(int(pointCount), config.area_name)
    print(f"Drew graph with {pointCount} points")
    shutil.move(currDir + '/temps.log', currDir + '/static/temps.log')
    try:
        with open(currDir + '/graph.png', 'rb') as ImageData:
            graphImageData = base64.b64encode(ImageData.read())
            graphImageData = graphImageData.decode('utf-8')
    except FileNotFoundError:
        graphImageData = ""
        print("File Not found")


    print('Updated Files')


    return render_template('tempreport.html', graphImageData=graphImageData, measureTemp=measureTemp, maxTemp=maxTemp, minTemp=minTemp, logContent=logContent, lineCount=lineCount, pointCount=pointCount, cpuTemp=str(cpu.temperature) + '°C')

if __name__ == "__main__":
    app.run(host= '0.0.0.0', port= 80)
