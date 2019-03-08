import time, csv, sys, os

counter = 0
delay = 0.5
choice = 0
cont = ''

def readFile():
  print()
  print("--------------------------------")
  print()
  with open('data/addresses.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 0
    for row in csv_reader:
        if line_count == 0:
            print(f'Addresses:')
            line_count += 1
        else:
            print(f'\t[{line_count}] - {row[0]}')
            line_count += 1
    print()
    global finalLine
    finalLine = line_count - 1
    print(f'Processed {line_count - 1} addresses, {line_count} lines')
    print()
    print("--------------------------------")
    print()

def addEntry():
  readFile()
  newAddress = str(input('Please enter the new address: '))
  print()
  print("--------------------------------")
  print()
  print('New line added')
  print()
  print("--------------------------------")
  print()
  time.sleep(delay)
  changes = [
    [newAddress],                                      
    ]
  with open('data/addresses.csv', 'a') as f:                                    
    writer = csv.writer(f)
    writer.writerows(changes)

def selectLine():
  readFile()
  global removeLineNumber
  global removeLine
  removeLineNumber = int(input('Please enter the line number to select: '))
  while removeLineNumber > finalLine:
    removeLineNumber = int(input('That line did not exist, please enter the line number to select: '))
  with open('data/addresses.csv', 'r') as csv_file:
    r = csv.reader(csv_file)
    for i in range(removeLineNumber):
        next(r)
    row = next(r)
    removeLine = str(row)
    removeLine = removeLine.replace("[", '')
    removeLine = removeLine.replace("]", '')
    removeLine = removeLine.replace("'", '')

def removeEntry():
  selectLine()
  f = open('data/addresses.csv','r')
  lines = f.readlines()
  f.close()
  f = open('data/addresses.csv','w')
  for line in lines:
    if line != removeLine + '\n':
      f.write(line)
  f.close()
  readFile()

def editEntry():
  selectLine()
  newLine = str(input('Please enter the changed line: '))
  f = open('data/addresses.csv','r')
  lines = f.readlines()
  f.close()
  f = open('data/addresses.csv','w')
  for line in lines:
    if line == removeLine + '\n':
      f.write(newLine)
    else:
      f.write(line)
  f.close()
  readFile()

def newDatabase():
  changes = [
    ['address'],
    ]
  checkDelete = str(input('Are you sure you want to erase the existing list and make a fresh one? (You may be seeing this message as the database never existed) Y/N: '))
  if checkDelete == 'Y':
    print("Deleting addresses and making new file")
    f = open('data/addresses.csv','w+')
    f.close()
    with open('data/addresses.csv', 'a') as f:                                    
      writer = csv.writer(f)
      writer.writerows(changes)
    print('Completed')
  else:
    print('Deletion aborted')
  print()
  print("--------------------------------")
  print()

def checkFile():
  if str(os.path.isfile('data/addresses.csv')) == 'False':
    newDatabase()

while counter == 0:
  print('Enter 1 to read the saved addresses')
  print('Enter 2 to add an entry')
  print('Enter 3 to delete an entry')
  print('Enter 4 to edit an entry')
  print('Enter 5 to generate a new address list')
  print('Enter 6 to exit')
  choice = str(input('Please make a choice: '))
  print()
  if choice == '1':
    checkFile()
    print('Reading file:')
    readFile()
    cont = input('Press any key to continue: ')
  elif choice == '2':
    checkFile()
    addEntry()
  elif choice == '3':
    checkFile()
    removeEntry()
  elif choice == '4':
    checkFile()
    editEntry()
  elif choice == '5':
    newDatabase()
  elif choice == '6':
    exit()
