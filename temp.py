import smtplib, datetime, time, csv, sys, os
import graph
from w1thermsensor import W1ThermSensor
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

#Variables for email and the sensor
email_recipients = ['example@gmail.com', 'example@gmail.com'] #Set recipient emails here if use_csv_recipient = 0
email_sender = 'example@gmail.com' #Set sender email here if use_csv_sender = 0
password = 'password' #Set sender email password here if use_csv_sender = 0
last_email_time = datetime.datetime(1970, 1, 1, 0, 0)
email_time_diff = 0
max_temp = 0
min_temp = 100
max_time = 0
min_time = 0
sensor = W1ThermSensor()

#See data/config.csv for a config file. Use python3 temp.py -c to generate a new one

def updateConfig(force):
  changes = [
    #DO NOT EDIT THESE, these are the default values when generating a new config
    ['config'],
    ['delay', '300'],
    ['gap', '3600'],
    ['threshold_max', '30'],
    ['threshold_min', '-1'],
    ['use_csv_recipient', '1'],
    ['use_csv_sender', '1'],
    ['graph_point_count', '12'],
    ]

  if force == 'y':
    print('\nGenerating config')
    f = open('data/config.csv','w+')
    f.close()
    with open('data/config.csv', 'a') as f:                                    
      writer = csv.writer(f)
      writer.writerows(changes)
    print('Generated new config')
    exit()

  if str(os.path.isfile('data/config.csv')) == 'False':
    print('\nGenerating config')
    f = open('data/config.csv','w+')
    f.close()
    with open('data/config.csv', 'a') as f:                                    
      writer = csv.writer(f)
      writer.writerows(changes)
    print('Generated new config')

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
          elif row[0] == 'gap':
            global gap
            gap = int(row[1])
            config_count += 1
          elif row[0] == 'threshold_max':
            global threshold_max
            threshold_max = int(row[1])
            config_count += 1
          elif row[0] == 'threshold_min':
            global threshold_min
            threshold_min = int(row[1])
            config_count += 1
          elif row[0] == 'use_csv_recipient':
            global use_csv_recipient
            use_csv_recipient = int(row[1])
            config_count += 1         
          elif row[0] == 'use_csv_sender':
            global use_csv_sender
            use_csv_sender = int(row[1])
            config_count += 1
          elif row[0] == 'graph_point_count':
            global graph_point_count
            graph_point_count = int(row[1])
            config_count += 1
          else:
            print('Invalid config line detected\n')
    print(f'Processed {config_count} config options, {line_count} lines\n')

def connectToServer():
  #Connects to gmail's servers
  global server
  server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
  server.connect('smtp.gmail.com', 465)
  print('Connected to server')
  server.login(email_sender, password)
  print('Logged in successfully as ' + email_sender + '\n')

def updateRecipients():
  try:
    with open('data/addresses.csv') as csv_file:
      csv_reader = csv.reader(csv_file, delimiter=',')
      line_count = 0
      for row in csv_reader:
          if line_count == 0:
              print('Addresses:')
              line_count += 1
          else:
              print(f'\t{row[0]}')
              if len(email_recipients) + 1 == line_count:
                email_recipients.append(str(row[0]))
              else:
                email_recipients[line_count - 1] = str(row[0])
              line_count += 1
    print(f'\nUsing CSV for recipient addresses, processed {line_count - 1} addresses, {line_count} lines')
  except FileNotFoundError:
    print("\nNo address file found, starting address editor: \n")
    import data_edit

def updateSender():
  global email_sender
  global password
  global email_sender_name
  try:
    with open('data/sender.csv') as csv_file:
      csv_reader = csv.reader(csv_file, delimiter=',')
      line_count = 0
      for row in csv_reader:
          if line_count == 0:
              line_count += 1
          elif line_count == 1:
              #Sender email
              email_sender = str(row[0])
              line_count += 1
          elif line_count == 2:
              #Sender password
              password = str(row[0])
              line_count += 1
          elif line_count == 3:
              #Sender name
              email_sender_name = str(row[0])
              line_count += 1
      print(f'Using CSV for credentials, processed {line_count - 1} credentials, {line_count} lines\n')
  except FileNotFoundError:
    changeSender('e')

def changeSender(mode):
  if str(os.path.isfile('data/sender.csv')) == 'False':
    print("We didn't find a sender credentials file, creating on for you:")
    changes = [
      ['details'],
      ['address'],
      ['password'],  
      ['name'], 
      ]
    f = open('data/sender.csv','w+')
    f.close()
    with open('data/sender.csv', 'a') as f:                                    
      writer = csv.writer(f)
      writer.writerows(changes)
    print('Done')
    changeSender('e')
    exit()

  if mode == 's':
    credential = input(str('Please enter the new email address: '))
    removeLineNumber = 1
    wFile = 1
  elif mode == 'p':
    credential = input(str('Please enter the new password: '))
    removeLineNumber = 2
    wFile = 1
  elif mode == 'n':
    credential = input(str('Please enter the new sender name: '))
    removeLineNumber = 3
    wFile = 1
  elif mode == 'e':
    print('\nPlease enter the sender details: \n')
    changeSender('s')
    changeSender('p')
    changeSender('n')
    wFile = 0

  if wFile == 1:
    with open('data/sender.csv', 'r') as csv_file:
      r = csv.reader(csv_file)
      for i in range(removeLineNumber):
          next(r)
      row = next(r)
      removeLine = str(row)
      removeLine = removeLine.replace("[", '')
      removeLine = removeLine.replace("]", '')
      removeLine = removeLine.replace("'", '')

    f = open('data/sender.csv','r')
    lines = f.readlines()
    f.close()
    f = open('data/sender.csv','w')
    for line in lines:
      if line == removeLine + '\n':
        f.write(credential + '\n')
      else:
        f.write(line)
    f.close()

def updateMessage():

  #Reads the image
  fp = open('graph.png', 'rb')
  html_image = MIMEImage(fp.read())
  fp.close()

  #Updates the message to be sent
  global msg
  currTime = datetime.datetime.now()
  msg = MIMEMultipart('alternative')
  msg['Subject'] = 'Temperature Alert'
  msg['From'] = email_sender_name
  msg['To'] = 'Whomever it may concern'
  html_wrap = '<html><body><p>The temperature is no longer between ' + str(threshold_max) + '°C and ' + str(threshold_min) + '°C. </p><p>The temperature is currently ' + str(temp) + '°C at ' + str(currTime.strftime("%H:%M:%S")) + '</p><br><img alt="Temperature Graph" id="graph" src="cid:graph"></body></html>'
  wrap = MIMEText(html_wrap, 'html')

  #Define the image's ID
  html_image.add_header('Content-ID', '<graph>')
  msg.attach(html_image)
  msg.attach(wrap)

def sendMessage():
  #Sends the message
  #Gets current time and works out time since the last email sent
  global last_email_time
  currTime = datetime.datetime.now()
  email_time_diff = (time.mktime(currTime.timetuple()) - time.mktime(last_email_time.timetuple()))
  #Sends the message if the time is ok
  if email_time_diff >= gap:
    #Sends an email to the addresses in the array
    for x in range(0, len(email_recipients)):
      server.sendmail(email_sender, email_recipients[x], msg.as_string())
      print('Email sent to ' + str(email_recipients[x]))
    print('Sent email to ' + str(len(email_recipients)) + ' addresses')
    print('Email was last sent ' + str(email_time_diff) + ' seconds ago')
    last_email_time = currTime
  else:
    print('Email was last sent ' + str(email_time_diff) + ' seconds ago')
    print("Email not sent\n")
  server.quit()
  print('\nLogged out\n')

def measureTemp():
  #Measures the temperature
  global temp
  print('Reading temperature:')
  temp = sensor.get_temperature()
  currTime = datetime.datetime.now()
  print('The temperature is ' + str(temp) + '°C at ' + str(currTime.strftime("%H:%M:%S")) + '\n')

def readCSVLine(filename, position, mode, line):
  if str(os.path.isfile(filename)) == 'False':
    return
  if mode == 'numbered':
    with open(filename, 'r') as csv_file:
      csv_reader = csv.reader(csv_file)
      for i in range(line):
          next(csv_reader)
      row = next(csv_reader)
      return row[position]
  elif mode == 'keyword':
    with open(filename) as csv_file:
      csv_reader = csv.reader(csv_file, delimiter=',')
      for row in csv_reader:
        if row[0] == line:
          return row[position]
  else:
    return

def logTemp():
  global temp
  global max_temp
  global min_temp
  if str(os.path.isfile('data/temp-records.csv')) == 'False':
    print("No report file found, creating one:")
    changes = [
      ['Temp-report report file:'],
      ['0', '0'],
      ['0', '0'],
      ]
    f = open('data/temp-records.csv','w+')
    f.close()
    with open('data/temp-records.csv', 'a') as f:
      writer = csv.writer(f)
      writer.writerows(changes)
    print('Report file created\n')

  currTime = datetime.datetime.now()
  currTime = currTime.strftime("%H:%M:%S")

  if temp > max_temp:
    max_temp = temp
    max_time = currTime
  else:
    max_temp = readCSVLine('data/temp-records.csv', 1, 'keyword', 'max')
    max_time = readCSVLine('data/temp-records.csv', 2, 'keyword', 'max')

  if temp < min_temp:
    min_temp = temp
    min_time = currTime
  else:
    min_temp = readCSVLine('data/temp-records.csv', 1, 'keyword', 'min')
    min_time = readCSVLine('data/temp-records.csv', 2, 'keyword', 'min')

  changes = [
    ['Temp-report report file:'],
    ['max', max_temp, max_time],
    ['min', min_temp, min_time],
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

  currTime = datetime.datetime.now()
  
  logLine = '[' + str(currTime.strftime("%c")) + '] Temperature: ' + str(temp) + '°C'
  changes = [
    [logLine],                                      
    ]
  with open('temps.log', 'a') as f:                                    
    writer = csv.writer(f)
    writer.writerows(changes)

sys.argv.append(0)
if sys.argv[1] == '-h' or sys.argv[1] == '--help':
  print('Options:')
  print('	-h | --help      : Display the help menu')
  print('	-a | --addresses : Add, remove, view or edit recipient email addresses')
  print('	-p | --password  : Update the password for the sender address used')
  print('	-s | --sender    : Change the address of the sender email')
  print('	-n | --name      : Change the name of the sender')
  print('	-c | --config    : Generate a new config file')
  exit()
elif sys.argv[1] == '-a' or sys.argv[1] == '--address':
  import data_edit
  exit()
elif sys.argv[1] == '-p' or sys.argv[1] == '--password':
  changeSender('p')
  exit()
elif sys.argv[1] == '-s' or sys.argv[1] == '--sender':
  changeSender('s')
  exit()
elif sys.argv[1] == '-n' or sys.argv[1] == '--name':
  changeSender('n')
  exit()
elif sys.argv[1] == '-c' or sys.argv[1] == '--config':
  updateConfig('y')
  exit()

print('--------------------------------')
counter = 0
while counter == 0:
  #Load the config
  updateConfig('n')
  #Measure the temperature
  measureTemp()
  logTemp()
  #Update addresses and credentials
  if temp >= threshold_max or temp <= threshold_min:
    if use_csv_recipient == 1:
      updateRecipients()
    if use_csv_sender == 1:
      updateSender()
    #Create message contents
    graph.generateGraph(graph_point_count, delay / 60)
    updateMessage()
    #Send the message
    connectToServer()
    sendMessage()
    print('--------------------------------\n')
  time.sleep(delay)
