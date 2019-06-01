#Contains shared functions for python scripts
import datetime, time, csv, sys, os, re, inspect
currDir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) + '/'
try:
  from w1thermsensor import W1ThermSensor
  sensor = W1ThermSensor()
except:
  print('Failed to load kernel modules, make sure you are running this on an RPI with OneWire and GPIO enabled')
  class sensor:
    def get_temperature():
      return 0

def getLineCount(filePath, output = False, title = 'Output:'):
  if output == True:
    output_count = getLineCount(filePath)
    print(title)
    for i in range(1, output_count + 1):
      line_output = readCSVLine(filePath, 1, 'numbered', i, var_type = 'str')
      print(f'  [{i}] - {line_output}')
    print()

  if str(os.path.isfile(filePath)) == 'False':
    return False
  else:
    lineCount = len(open(filePath).readlines(  ))
    return lineCount

def checkLineCount(filePath, lineCount):
  if str(os.path.isfile(filePath)) == 'False':
    return False
  if lineCount >= len(open(filePath).readlines(  )):
    return True
  else:
    return False

def readLine(filename, mode, line, **kwargs):
  char = ''
  var_type = ''
  value = None
  for key, value in kwargs.items():
    if key == 'char':
      char = str(value)
    elif key == 'var_type' or key == 'data_type' or key == 'type':
      var_type = str(value)
  if str(os.path.isfile(filename)) == 'False':
    return
  if mode == 'numbered':
    with open(filename, 'r') as f:
      reader = f.readlines()
      value = reader[line - 1]
  elif mode == 'keyword':
    with open(filename, 'r') as f:
      reader = f.readlines()
      for row in range(len(reader)):
        if reader[row].find(str(line)) == 0:
          value = reader[row]
  else:
    return
  if char != '':
    value = value.strip()
    value = re.split(str(char), value)
    value = value[len(value) - 1]
  if var_type == 'str':
    return str(value)
  elif var_type == 'int':
    return int(value)
  elif var_type == 'float':
    return float(value)
  else:
    return value

def readCSVLine(filename, position, mode, line, **kwargs):
  var_type = ''
  value = None
  for key, value in kwargs.items():
    if key == 'var_type' or key == 'data_type' or key == 'type':
      var_type = str(value)
  if str(os.path.isfile(filename)) == 'False':
    return
  if position == 0:
    return
  try:
    if mode == 'numbered':
      with open(filename, 'r') as f:
        reader = csv.reader(f)
        for i in range(int(line) - 1):
            next(reader)
        row = next(reader)
        value = row[position - 1]
    elif mode == 'keyword':
      with open(filename) as f:
        reader = csv.reader(f, delimiter=',')
        for row in reader:
          if row[0] == line:
            value = row[position - 1]
    else:
      return
    if var_type == 'str':
      return str(value)
    elif var_type == 'int':
      return int(value)
    elif var_type == 'float':
      return float(value)
    else:
      return value
  except StopIteration:
    print("That line doesn't exist")
    return
  except IndexError:
    print("That position doesn't exist")
    return

def writeConfig(mode):
  changes = [
    #DO NOT EDIT THESE, these are the default values when generating a new config and will be overwritten by an update
    ['config'],
    ['delay', '300'], #Delay between each temperature reading in seconds, must be 60+
    ['gap', '3600'], #Delay between emails
    ['threshold_max', '30'], #Max temp for emailing
    ['threshold_min', '-1'], #Min temp for emailing
    ['graph_point_count', '12'], #Amount of points on graphs
    ]

  if mode == 'f':
    print('Generating config')
    f = open('data/config.csv','w+')
    f.close()
    with open('data/config.csv', 'a') as f:
      writer = csv.writer(f, lineterminator="\n")
      writer.writerows(changes)
    print('Generated new config\n')
    return
  elif mode == 's':
    if str(os.path.isfile('data/config.csv')) == 'False':
      writeConfig('f')
    add_count = 0
    remove_count = 0
    for count in range(1, len(changes)):
      searchLine = changes[count][0]
      success = 0
      with open('data/config.csv') as f:
        reader = csv.reader(f, delimiter=',')
        for row in reader:
          if row[0] == 'config':
            config_count = 0
          elif row[0] == searchLine:
            success = 1
        if success == 0:
          print(searchLine + ' was not found')
          print(changes[count][1])
          remove_count += 1
          with open('data/config.csv', 'a') as f:
            writer = csv.writer(f, lineterminator="\n")
            config_add=[searchLine, changes[count][1]]
            writer.writerow(config_add)
        else:
          success = 0

    with open('data/config.csv') as f:
      reader = csv.reader(f, delimiter=',')
      line_count = 0
      for row in reader:
          if row[0] == 'config':
              config_count  = 0
          else:
              for count in range(1, len(changes)):
                searchLine = changes[count][0]
                if row[0] == searchLine:
                  success = 1
              if success == 0:
                remove_count += 1
                print(str(row[0]))
                removeLine = str(row)
                removeLine = removeLine.replace("[", '').replace("]", '').replace("'", '').replace(", ", ',')
                with open('data/config.csv','r') as f:
                  lines = f.readlines()
                with open('data/config.csv','w') as f:
                  for line in lines:
                    if line != removeLine + '\n':
                      f.write(line)
              if success == 1:
                success = 0
      print(f'\nRemoved {remove_count} config lines, added {add_count} config lines')

    return
  else:
    return

def measureTemp(mode = 'V'):
  print('Reading temperature:')
  temp = round(float(sensor.get_temperature()), 2)
  if mode == 'V':
    print('The temperature is ' + str(temp) + '°C at ' + str(datetime.datetime.now().strftime("%H:%M:%S")) + '\n')
  return temp

def checkAddresses():
  if str(os.path.isfile('data/addresses.csv')) == 'False':
    newDatabase()

def appendLine(filePath, data):
  changes = [
    [data],
    ]
  if str(os.path.isfile(filePath)) == 'False':
    with open(filePath, 'w+') as f:
      writer = csv.writer(f, lineterminator="\n")
      writer.writerow(changes[0])
      return
  else:
    with open(filePath, 'a') as f:
      writer = csv.writer(f, lineterminator="\n")
      writer.writerow(changes[0])
      return

def removeLine(filePath):
  replaceLine = selectLine(filePath)
  print()
  with open(filePath, 'r') as f:
    lines = f.readlines()
  with open(filePath, 'w') as f:
    for line in lines:
      if line == replaceLine + '\n' or line == replaceLine:
        print('Removing line')
      else:
        f.write(line)

def editLine(filePath):
  replaceLine = selectLine(filePath)
  newLine = str(input('Please enter the changed line: '))
  print()
  with open(filePath, 'r') as f:
    lines = f.readlines()
  with open(filePath, 'w') as f:
    for line in lines:
      if line == replaceLine + '\n' or line == replaceLine:
        f.write(newLine + '\n')
      else:
        f.write(line)

def selectLine(filePath):
  getLineCount(filePath, True, 'Addresses:')
  selectLineNumber = int(input('Please enter the line number to select: ')) - 1
  finalLine = getLineCount(filePath)
  while selectLineNumber > finalLine:
    selectLineNumber = int(input('That line did not exist, please enter the line number to select: '))
  with open(filePath, 'r') as f:
    reader = csv.reader(f)
    for i in range(selectLineNumber):
        next(reader)
    row = next(reader)
    selectLineVal = str(row[0])
    return str(selectLineVal)

def newFile(filePath, firstLine):
  changes = [
    [firstLine],
    ]
  if str(os.path.isfile(filePath)) == 'True':
    confirmDelete = str(input('Are you sure you want to erase the existing list and make a fresh one? (Y/N): '))
  else:
    confirmDelete = 'Y'
  if confirmDelete == 'Y':
    print("\nMaking new file:\n")
    with open(filePath,'w+') as f:
      writer = csv.writer(f, lineterminator="\n")
      writer.writerow(changes[0])
    print('Completed\n')
  else:
    print('Deletion aborted\n')
  print("--------------------------------\n")

def checkAddressLine():
  if readCSVLine('data/addresses.csv', 1, 'keyword', 'addresses') == None:
    replaceLine = readCSVLine('data/addresses.csv', 1, 'numbered', '1')
    with open('data/addresses.csv', 'r') as f:
      lines = f.readlines()
    with open('data/addresses.csv', 'w') as f:
      for line in lines:
        if line == replaceLine + '\n' or line == replaceLine:
          f.write('addresses\n')
          f.write(line)
        else:
          f.write(line)
  else:
    return

def dataEdit():
  while True:
    print('Enter 1 to read the saved addresses')
    print('Enter 2 to add an entry')
    print('Enter 3 to delete an entry')
    print('Enter 4 to edit an entry')
    print('Enter 5 to generate a new address list')
    print('Enter 6 to exit')
    choice = str(input('Please make a choice: '))
    print('\n--------------------------------\n')
    if choice == '1':
      checkAddresses()
      print('Reading file:\n')
      getLineCount('data/addresses.csv', True, 'Addresses:')
      input('Press any key to continue: \n')
    elif choice == '2':
      checkAddresses()
      getLineCount('data/addresses.csv', True, 'Addresses:')
      newAddress = str(input('Please enter the new address: '))
      appendLine('data/addresses.csv', newAddress)
      print("\n--------------------------------\n")
      print('New line added')
      print("\n--------------------------------\n")
    elif choice == '3':
      checkAddresses()
      removeLine('data/addresses.csv')
      print("\n--------------------------------\n")
      print('Line removed')
      print("\n--------------------------------\n")
    elif choice == '4':
      checkAddresses()
      editLine('data/addresses.csv')
      print("\n--------------------------------\n")
      getLineCount('data/addresses.csv', True, 'Addresses:')
      print("--------------------------------\n")
    elif choice == '5':
      newFile('data/addresses.csv', 'addresses')
    elif choice == '6':
      checkAddressLine()
      exit()
