#Contains shared functions for python scripts
import datetime, csv, os, inspect

currDir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) + '/'

try:
  from w1thermsensor import W1ThermSensor
  sensor = W1ThermSensor()
except:
  print('Failed to load kernel modules, make sure you are running this on an RPI with OneWire and GPIO enabled')
  class sensor:
    def get_temperature():
      return 0

def readCSVLine(filename, position, mode, line):
  #Check the file exists
  if os.path.isfile(filename) == False:
    return None

  #Check the position isn't 0
  if position == 0:
    return None

  #Attempt to find the requested line
  try:
    #Find the specified line number
    if mode == 'numbered':
      with open(filename, 'r') as f:
        reader = csv.reader(f)
        #Loop until the given line is next
        for i in range(int(line) - 1):
            next(reader)
        #Save the contents of the correct position of the line
        row = next(reader)
        value = row[position - 1]
    #Return the first line where the first position matches the keyword
    elif mode == 'keyword':
      with open(filename) as f:
        reader = csv.reader(f, delimiter=',')
        #Loop through each line, and check first element against search string
        for row in reader:
          if row[0] == line:
            value = row[position - 1]
    else:
      #Return nothing if no mode was given
      return None
    return value
  #Error handling for missing lines and positions
  except StopIteration:
    print("That line doesn't exist")
    return None
  except IndexError:
    print("That position doesn't exist")
    return None
  except UnboundLocalError:
    print("That keyword doesn't exist")
    return None

def measureTemp(mode = 'V'):
  print('Reading temperature:')
  temp = round(float(sensor.get_temperature()), 2)
  if mode == 'V':
    print('The temperature is ' + str(temp) + '°C at ' + str(datetime.datetime.now().strftime("%H:%M:%S")) + '\n')
  return temp

def updateRecords(temp):
  temp.max.value = float(readCSVLine('data/temp-records.csv', 2, 'keyword', 'max'))
  temp.max.time = str(readCSVLine('data/temp-records.csv', 3, 'keyword', 'max'))
  if float(temp.current.value) > float(temp.max.value):
    print('Current temp was higher than recorded max temp, updating locally\n')
    temp.max.value = temp.current.value
    temp.max.time = datetime.datetime.now().strftime("%H:%M:%S")

  temp.min.value = float(readCSVLine('data/temp-records.csv', 2, 'keyword', 'min'))
  temp.min.time = str(readCSVLine('data/temp-records.csv', 3, 'keyword', 'min'))
  if float(temp.current.value) < float(temp.min.value):
    print('Current temp was lower than recorded min temp, updating locally\n')
    temp.min.value = temp.current.value
    temp.min.time = datetime.datetime.now().strftime("%H:%M:%S")

  return temp

def returnNewTemp():
  class temp:
    class template(object):
      value=0.0
      time=0
    class current(template):
      pass
    class max(template):
      pass
    class min(template):
      pass
  return temp
