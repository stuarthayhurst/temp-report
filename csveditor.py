import os
import tempreport

#Make a new address list if missing
def checkAddressFile():
  if os.path.isfile('data/addresses.list') == False:
    newFile('data/addresses.list')

#Create a blank file at the specified path
def newFile(filePath):
  with open(filePath, 'w'):
    pass

#Display the contents of a given file
def displayFile(filePath):
  print('Addresses:')
  for i in range(1, len(open(filePath).readlines()) + 1):
    lineOutput = str(tempreport.readCSVLine(filePath, 1, 'numbered', i))
    print(f'  [{i}] - {lineOutput}')
  print('')

#Add data to the end of filePath
def appendLine(filePath, data):
  with open(filePath, 'a') as f:
    f.write(data + '\n')

#Delete an address / line number from filePath
def removeLine(filePath, selectedLine):
  #Get all the lines in the file to iterate through
  with open(filePath, 'r') as f:
    lines = f.readlines()

  #Loop through all the lines, and write them back to the file if they aren't to be removed
  with open(filePath, 'w') as f:
    for lineNum in range(0, len(lines)):
      currentLine=lines[lineNum]
      #Skip rewriting line if it's the line to remove
      if currentLine == selectedLine + '\n' or currentLine == selectedLine or str(lineNum + 1) == selectedLine:
        print('Removing line')
      else:
        f.write(currentLine)

#Change the line at position selectedLine in filePath
def editLine(filePath, selectedLine):
  newLine = str(input('Please enter the updated line: '))
  print('')
  with open(filePath, 'r') as f:
    lines = f.readlines()
  with open(filePath, 'w') as f:
    for lineNum in range(0, len(lines)):
      currentLine=lines[lineNum]
      if currentLine == selectedLine + '\n' or currentLine == selectedLine or str(lineNum + 1) == selectedLine:
        f.write(newLine + '\n')
      else:
        f.write(currentLine)

#Main loop to edit address list
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

    #Check the file exists before attempting to use it
    checkAddressFile()

    if choice == '1': #Display contents of the address list file
      print('Reading file:\n')
      displayFile('data/addresses.list')
      input()
    elif choice == '2': #Add a new line to the file
      displayFile('data/addresses.list')
      newAddress = str(input('Please enter the new address: '))
      appendLine('data/addresses.list', newAddress)
      print("\n--------------------------------\n")
      print('New line added')
      print("\n--------------------------------\n")
    elif choice == '3': #Remove a line from the file
      displayFile('data/addresses.list')
      selectedLine = str(input('Please enter a line number or address to remove: '))
      removeLine('data/addresses.list', selectedLine)
      print("\n--------------------------------\n")
      print('Line removed')
      print("\n--------------------------------\n")
    elif choice == '4': #Edit a line from the file
      displayFile('data/addresses.list')
      selectedLine = str(input('Please enter a line number or address to edit: '))
      editLine('data/addresses.list', selectedLine)
    elif choice == '5': #Reset the file
      confirmReset = str(input('Are you sure you want to erase the address list and start again? (Y/n) '))
      if confirmReset.lower() == "y":
        newFile('data/addresses.list')
      else:
        print('Aborted')
      print("\n--------------------------------\n")
    elif choice == '6': #Exit program
      exit()
    else:
      input('Invalid choice')

def changeSender(mode):
  #Prompt creation of new file if missing
  if os.path.isfile('data/sender.info') == False and mode != "create":
    print("We didn't find a sender credentials file, creating one for you...")
    changeSender('create')
    exit()

  #Create file with lines for data to fill, if missing
  if os.path.isfile('data/sender.info') == False:
    placeholder = ['address', 'password', 'name']
    with open('data/sender.info', 'w') as f:
      for line in placeholder:
        f.write(line + "\n")

  #Input information to write to file
  if mode == 'sender':
    credential = input(str('Please enter the new email address: '))
    editLineNumber = 0
  elif mode == 'password':
    credential = input(str('Please enter the new password: '))
    editLineNumber = 1
  elif mode == 'name':
    credential = input(str('Please enter the new sender name: '))
    editLineNumber = 2
  elif mode == 'create':
    print('\nPlease enter the sender details:')
    changeSender('sender')
    changeSender('password')
    changeSender('name')
    return

  #Write entered data to file
  with open('data/sender.info','r') as f:
    lines = f.readlines()
  with open('data/sender.info','w') as f:
    for lineNum in range(0, len(lines)):
      if editLineNumber == lineNum:
        f.write(credential + "\n")
      else:
        f.write(lines[lineNum])
