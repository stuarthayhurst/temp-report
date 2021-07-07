import datetime, time, csv, os, re, sys
from tzlocal import get_localzone
import commonfuncs as tempreport

def logTemp():
  global temp
  global logDateTimeFormat
  global midnight

  #Get current time
  curr_time = time.mktime(datetime.datetime.now().timetuple())
  tz = get_localzone()
  print('Current time: ' + str(datetime.datetime.now()) + '\n')

  #Decide if it's within (config.log_intervel * 1.5) past midnight, and trigger record reset
  if curr_time > midnight and curr_time < midnight + (config.log_interval * 1.5):
    midnight = datetime.datetime.combine(datetime.date.today() + datetime.timedelta(days=1), datetime.time())
    midnight = time.mktime(midnight.timetuple())
    print('Time is ' + str(datetime.datetime.now()) + ' (Midnight), resetting record values')
    temp.max.value = -100.0
    temp.min.value = 999.9
    print('Records reset\n')

  #Work out if current temperature is the highest recently, and set variables accordingly
  if float(temp.current.value) > float(temp.max.value):
    print('Set new max temperature\n')
    temp.max.value = temp.current.value
    temp.max.time = datetime.datetime.now().strftime("%H:%M:%S")
  else:
    temp.max.value = float(tempreport.readCSVLine('data/temp-records.csv', 2, 'keyword', 'max'))
    temp.max.time = str(tempreport.readCSVLine('data/temp-records.csv', 3, 'keyword', 'max'))

  #Work out if current temperature is the lowest recently, and set variables accordingly
  if float(temp.current.value) < float(temp.min.value):
    print('Set new min temperature\n')
    temp.min.value = temp.current.value
    temp.min.time = datetime.datetime.now().strftime("%H:%M:%S")
  else:
    temp.min.value = float(tempreport.readCSVLine('data/temp-records.csv', 2, 'keyword', 'min'))
    temp.min.time = str(tempreport.readCSVLine('data/temp-records.csv', 3, 'keyword', 'min'))

  #Format records for writing
  changes = [
    ['max', temp.max.value, temp.max.time],
    ['min', temp.min.value, temp.min.time],
  ]

  #Write records to a file
  with open('data/temp-records.csv', 'w') as f:
      writer = csv.writer(f, lineterminator="\n")
      writer.writerows(changes)

  #Format and write a new logline
  date = datetime.datetime.now().strftime(logDateTimeFormat)
  logline = f'[{date}] {temp.current.value}'
  changes = [
    [logline],
  ]
  with open('temps.log', 'a') as f:
    writer = csv.writer(f, lineterminator="\n")
    writer.writerows(changes)

#Load config
while os.path.isfile('data/config.py') == False:
  time.sleep(1)
sys.path.insert(1, 'data/')
import config
print("Loaded config")

#Wait for correct time to resume logging
if os.path.isfile('temps.log') == True:
  logDateTimeFormat  = '%Y-%m-%d %H:%M:%S'
  curr_time = time.mktime(datetime.datetime.now().timetuple())
  with open('temps.log', 'r') as f:
    data = f.readlines() [-1:]
    print('\nLast log entry: ' + data[0])
    data = re.split("\[(.*?)\]", data[0])
    last_time = time.mktime(datetime.datetime.strptime(data[1], logDateTimeFormat).timetuple())
  if curr_time > last_time + config.log_interval:
    pass
  else:
    print('Waiting for correct time to resume logging...')
    with open('temps.log', 'r') as f:
      data = f.readlines() [-1:]
      data = re.split("\[(.*?)\]", data[0])
      last_time = time.mktime(datetime.datetime.strptime(data[1], logDateTimeFormat).timetuple())
    while curr_time < last_time + config.log_interval:
        curr_time = time.mktime(datetime.datetime.now().timetuple())
        time.sleep(1)

#Create temp class to store temperatures and times
temp = tempreport.returnNewTemp()

#Set extreme opposite values to trigger a refresh
temp.max.value = -100.0
temp.min.value = 999.9

#Datetime format for temps.log
logDateTimeFormat = '%Y-%m-%d %H:%M:%S'

#Calculate time of next midnight
midnight = datetime.datetime.combine(datetime.date.today() + datetime.timedelta(days=1), datetime.time())
midnight = time.mktime(midnight.timetuple())

while True:
  #Measure the temperature
  temp.current.value = tempreport.measureTemp()
  logTemp()
  print('--------------------------------\n')
  time.sleep(config.log_interval)
