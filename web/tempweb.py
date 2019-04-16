from flask import Flask, render_template, url_for
import flask, random, os, sys, inspect, shutil, time
app = Flask(__name__, static_url_path='/static')

try:
    from w1thermsensor import W1ThermSensor
    sensor = W1ThermSensor()
except:
    print('Failed to load kernel modules, make sure you are running this on an RPI with OneWire and GPIO enabled')

currDir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parDir = os.path.dirname(currDir)
sys.path.insert(0,parDir)
import graph, tempreport

readme = parDir + '/README.md'
tempWebVer = tempreport.readLine(readme, 'keyword', 'Temp-web', char = ': ')
tempVer = tempreport.readLine(readme, 'keyword', 'Temp-report', char = ': ')

shutil.copy2(parDir + '/temps.log', currDir + '/temps.log')
graph.generateGraph(tempreport.readCSVLine(parDir + '/data/config.csv', 2, 'keyword', 'graph_point_count', var_type = 'int'))
shutil.move(currDir + '/temps.log', currDir + '/static/temps.log')
shutil.move(currDir + '/graph.png', currDir + '/static/graph.png')

@app.route('/')
def main(flaskVer=flask.__version__, tempWebVer=tempWebVer, tempVer=tempVer):
    def measureTemp():
        return random.randint(1,30)#str(sensor.get_temperature()) + '°C'
    with open(currDir + '/static/temps.log', "r") as f:
        logContent = f.read()
    return render_template('tempreport.html', flaskVer=flaskVer, tempWebVer=tempWebVer, tempVer=tempVer, measureTemp=measureTemp, logContent=logContent)

if __name__ == "__main__":
    app.run(host= '0.0.0.0', port= 5000)
