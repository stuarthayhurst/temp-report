
from flask import Flask, render_template, url_for
#from w1thermsensor import W1ThermSensor
import flask
app = Flask(__name__, static_url_path='/static')
#sensor = W1ThermSensor()
tempVer= '0.0.6'

@app.route('/')
def main(flaskVer= flask.__version__, tempVer= tempVer):
    def measureTemp():
        return 'Test'
        return sensor.get_temperature()
    return render_template('tempreport.html', flaskVer=flaskVer, tempVer=tempVer, measureTemp=measureTemp)

if __name__ == "__main__":
    app.run()
