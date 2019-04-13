#Contains shared functions for python scripts

import os, datetime, time, csv

def checkLineCount(filePath, lineCount):
  if lineCount == len(open(filePath).readlines(  )):
    return True
  else:
    return False

def readCSVLine(filename, position, mode, line):
  if str(os.path.isfile(filename)) == 'False':
    return
  if mode == 'numbered':
    with open(filename, 'r') as f:
      reader = csv.reader(f)
      for i in range(line):
          next(reader)
      row = next(reader)
      return row[position]
  elif mode == 'keyword':
    with open(filename) as f:
      reader = csv.reader(f, delimiter=',')
      for row in reader:
        if row[0] == line:
          return row[position]
  else:
    return

def writeConfig(mode):
  changes = [
    #DO NOT EDIT THESE, these are the default values when generating a new config
    ['config'],
    ['delay', '300'], #Delay between each temperature reading
    ['gap', '3600'], #Delay between emails
    ['threshold_max', '30'], #Max temp for emailing
    ['threshold_min', '-1'], #Min temp for emailing
    ['graph_point_count', '12'], #Amount of points on graphs
    ['record_reset', '24'], #Time between mix and max temp reset in hours
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
                removeLine = removeLine.replace("[", '')
                removeLine = removeLine.replace("]", '')
                removeLine = removeLine.replace("'", '')
                removeLine = removeLine.replace(", ", ',')
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
