
from flask import Flask, render_template, url_for
#from w1thermsensor import W1ThermSensor
import flask
app = Flask(__name__, static_url_path='/static')
#sensor = W1ThermSensor()
tempVer= '0.0.7'

@app.route('/')
def main(flaskVer= flask.__version__, tempVer= tempVer):
    def measureTemp():
        return sensor.get_temperature() + '°C'
    return render_template('tempreport.html', flaskVer=flaskVer, tempVer=tempVer, measureTemp=measureTemp)

if __name__ == "__main__":
    app.run(host= '0.0.0.0')
