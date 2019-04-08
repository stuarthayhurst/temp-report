import datetime, time, os, csv
import tempreport
from w1thermsensor import W1ThermSensor

record_reset_time = datetime.datetime(1970, 1, 1, 0, 0)
max_temp = -100.0
min_temp = 999.9
max_temp_time = 0
min_temp_time = 0
sensor = W1ThermSensor()

def updateConfig():
  with open('data/config.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    config_count = 0
    line_count = 0
    for row in csv_reader:
        if line_count == 0:
          print('Reading config')
          line_count += 1
        else:
          if row[0] == 'delay':
            global delay
            delay = int(row[1])
            config_count += 1
          elif row[0] == 'record_reset':
            global record_reset
            record_reset = int(row[1])
            record_reset = record_reset * 3600
            config_count += 1
    print(f'Processed {config_count} config options, {line_count} lines\n')

def logTemp():
  global temp
  global max_temp
  global min_temp
  global max_temp_time
  global min_temp_time
  global record_reset
  global record_reset_time

  if str(os.path.isfile('data/temp-records.csv')) == 'False':
    print("No report file found, creating one:")
    changes = [
      ['Temp-report report file:'],
      ['max', '0', '0'],
      ['min', '0', '0'],
      ]
    f = open('data/temp-records.csv','w+')
    f.close()
    with open('data/temp-records.csv', 'a') as f:
      writer = csv.writer(f)
      writer.writerows(changes)
    print('Report file created\n')

  currTime = datetime.datetime.now()
  time_diff = (time.mktime(currTime.timetuple()) - time.mktime(record_reset_time.timetuple()))
  if time_diff >= record_reset:
    record_reset_time = datetime.datetime.now()
    print(str(record_reset) + ' Hours have passed since last record reset, resetting record values')
    max_temp = -100.0
    min_temp = 999.9
    print('Records reset\n')

  if float(temp) > float(max_temp):
    print('Set new max temperature\n')
    max_temp = temp
    max_temp_time = currTime.strftime("%H:%M:%S")
  else:
    max_temp = tempreport.readCSVLine('data/temp-records.csv', 1, 'keyword', 'max')
    max_temp_time = tempreport.readCSVLine('data/temp-records.csv', 2, 'keyword', 'max')

  if float(temp) < float(min_temp):
    print('Set new min temperature\n')
    min_temp = temp
    min_temp_time = currTime.strftime("%H:%M:%S")
  else:
    min_temp = tempreport.readCSVLine('data/temp-records.csv', 1, 'keyword', 'min')
    min_temp_time = tempreport.readCSVLine('data/temp-records.csv', 2, 'keyword', 'min')

  changes = [
    ['Temp-report report file:'],
    ['max', max_temp, max_temp_time],
    ['min', min_temp, min_temp_time],
    ]

  with open('data/temp-records.csv', 'w') as f:
      writer = csv.writer(f)
      writer.writerows(changes)

  if str(os.path.isfile('./temps.log')) == 'False':
    print("No log found, creating one:")
    changes = [
      ['Temp-report logfile:'],
      ]
    f = open('temps.log','w+')
    f.close()
    with open('temps.log', 'a') as f:                                    
      writer = csv.writer(f)
      writer.writerows(changes)
    print('Log created\n')
  
  logLine = '[' + str(currTime.strftime("%c")) + '] Temperature: ' + str(temp) + '°C'
  changes = [
    [logLine],                                      
    ]
  with open('temps.log', 'a') as f:                                    
    writer = csv.writer(f)
    writer.writerows(changes)


def measureTemp():
  #Measures the temperature
  global temp
  print('Reading temperature:')
  temp = float(sensor.get_temperature())
  currTime = datetime.datetime.now()
  print('Temperature ' + str(temp) + '°C at ' + str(currTime.strftime("%H:%M:%S")) + '\n' + 'Added to log\n')


counter = 0
while counter == 0:
  #Load the config
  if str(os.path.isfile('data/config.csv')) == 'True':
    updateConfig()
    #Measure the temperature
    measureTemp()
    logTemp()
  else:
    print('No config file found, skipping run')
  print('--------------------------------\n')
  time.sleep(delay)
