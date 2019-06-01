import datetime, time, pytz, csv, os
from tzlocal import get_localzone
import tempreport

record_reset_time = datetime.datetime(1970, 1, 1, 0, 0)
max_temp = -100.0
min_temp = 999.9

def updateConfig():

  global delay
  delay = tempreport.readCSVLine('data/config.csv', 2, 'keyword', 'delay', var_type = 'int')

  if delay == None:
    print('Errors occured while reading config values, attempting to fix config file:')
    tempreport.writeConfig('s')
    print('Done')
    updateConfig()
  print('Read config values')

def logTemp():
  global temp
  global max_temp
  global min_temp
  global max_temp_time
  global min_temp_time

  if str(os.path.isfile('data/temp-records.csv')) == 'False':
    print('No report file found, creating one:')
    changes = [
      ['Temp-report report file:'],
      ['max', '0', '0'],
      ['min', '0', '0'],
      ]
    f = open('data/temp-records.csv','w+')
    f.close()
    with open('data/temp-records.csv', 'a') as f:
      writer = csv.writer(f, lineterminator="\n")
      writer.writerows(changes)
    print('Report file created\n')

  curr_time = time.mktime(datetime.datetime.now().timetuple())
  tz = get_localzone() 
  midnight = datetime.datetime.combine(datetime.date.today() + datetime.timedelta(days=1), datetime.time())
  midnight = time.mktime(midnight.timetuple())
  print('Current time: ' + str(curr_time))
  print('Midnight: ' + str(midnight))
  if curr_time > midnight and curr_time < midnight + delay * 1.5:
    print('Time is ' + str(datetime.datetime.now()) + ' (Midnight), resetting record values')
    max_temp = -100.0
    min_temp = 999.9
    print('Records reset\n')

  if float(temp) > float(max_temp):
    print('Set new max temperature\n')
    max_temp = temp
    max_temp_time = datetime.datetime.now().strftime("%H:%M:%S")
  else:
    max_temp = tempreport.readCSVLine('data/temp-records.csv', 2, 'keyword', 'max', var_type = 'float')
    max_temp_time = tempreport.readCSVLine('data/temp-records.csv', 3, 'keyword', 'max')

  if float(temp) < float(min_temp):
    print('Set new min temperature\n')
    min_temp = temp
    min_temp_time = datetime.datetime.now().strftime("%H:%M:%S")
  else:
    min_temp = tempreport.readCSVLine('data/temp-records.csv', 2, 'keyword', 'min', var_type = 'float')
    min_temp_time = tempreport.readCSVLine('data/temp-records.csv', 3, 'keyword', 'min')

  changes = [
    ['Temp-report report file:'],
    ['max', max_temp, max_temp_time],
    ['min', min_temp, min_temp_time],
    ]

  with open('data/temp-records.csv', 'w') as f:
      writer = csv.writer(f, lineterminator="\n")
      writer.writerows(changes)

  if str(os.path.isfile('./temps.log')) == 'False':
    print('No log found, creating one:')
    changes = [
      ['Temp-report logfile:'],
      ]
    f = open('temps.log','w+')
    f.close()
    with open('temps.log', 'a') as f:                                    
      writer = csv.writer(f, lineterminator="\n")
      writer.writerows(changes)
    print('Log created\n')
  
  logLine = '[' + str(datetime.datetime.now().strftime("%c")) + '] Temperature: ' + str(temp) + '°C'
  changes = [
    [logLine],                                      
    ]
  with open('temps.log', 'a') as f:                                    
    writer = csv.writer(f, lineterminator="\n")
    writer.writerows(changes)

while str(os.path.isfile('data/config.csv')) == 'False':
  time.sleep(1)

while True:
  #Load the config
  updateConfig()
  #Measure the temperature
  temp = tempreport.measureTemp()
  logTemp()
  print('--------------------------------\n')
  time.sleep(delay)
