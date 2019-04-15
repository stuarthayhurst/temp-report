import smtplib, datetime, time, csv, sys, os
import tempreport
import graph
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

#Variables for email and the sensor
email_recipients = ['']
email_sender = ''
password = ''
last_email_time = datetime.datetime(1970, 1, 1, 0, 0)
record_reset_time = datetime.datetime(1970, 1, 1, 0, 0)
email_time_diff = 0
max_temp = -100.0
min_temp = 999.9
max_temp_time = 0
min_temp_time = 0

#See data/config.csv for a config file. Use python3 temp.py -c to generate a new one

def updateConfig():
  global delay
  delay = tempreport.readCSVLine('data/config.csv', 2, 'keyword', 'delay', 'int')
  global gap
  gap = tempreport.readCSVLine('data/config.csv', 2, 'keyword', 'gap', 'int')
  global threshold_max
  threshold_max = tempreport.readCSVLine('data/config.csv', 2, 'keyword', 'threshold_max', 'float')
  global threshold_min
  threshold_min = tempreport.readCSVLine('data/config.csv', 2, 'keyword', 'threshold_min', 'float')
  global graph_point_count
  graph_point_count = tempreport.readCSVLine('data/config.csv', 2, 'keyword', 'graph_point_count', 'int')
  global record_reset
  record_reset = tempreport.readCSVLine('data/config.csv', 2, 'keyword', 'record_reset', 'int') * 3600

  if delay == None:
    print('Errors occured while reading config values, attempting to fix config file:')
    tempreport.writeConfig('s')
    print('Done')
    updateConfig()
  print('Read config values')

def connectToServer():
  #Connects to gmail's servers
  global server
  server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
  server.connect('smtp.gmail.com', 465)
  print('Connected to server')
  server.login(email_sender, password)
  print('Logged in successfully as ' + email_sender + '\n')

def updateRecipients():
  if str(os.path.isfile('data/addresses.csv')) == 'False':
    print('\nNo address file found, starting address editor: \n')
    tempreport.dataEdit()
  print('Addresses:')
  line_count = tempreport.getLineCount('data/addresses.csv')
  for line in range(2, line_count + 1):
    if line == 2:
      email_recipients[0] = (tempreport.readCSVLine('data/addresses.csv', 1, 'numbered', line, 'str'))
      print(email_recipients[0])
    else:
      email_recipients.append(tempreport.readCSVLine('data/addresses.csv', 1, 'numbered', line, 'str'))
      print(email_recipients[line - 2])

def updateSender():
  global email_sender_name
  global email_sender
  global password
  if str(os.path.isfile('data/sender.csv')) == 'False':
    changeSender('e')
  email_sender      = tempreport.readCSVLine('data/sender.csv', 1, 'numbered', 2, 'str')
  password          = tempreport.readCSVLine('data/sender.csv', 1, 'numbered', 3, 'str')
  email_sender_name = tempreport.readCSVLine('data/sender.csv', 1, 'numbered', 4, 'str')

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
      writer = csv.writer(f, lineterminator="\n")
      writer.writerows(changes)
    print('Done')
    changeSender('e')
    exit()

  if mode == 's':
    credential = input(str('Please enter the new email address: '))
    selectLineNumber = 1
    wFile = 1
  elif mode == 'p':
    credential = input(str('Please enter the new password: '))
    selectLineNumber = 2
    wFile = 1
  elif mode == 'n':
    credential = input(str('Please enter the new sender name: '))
    selectLineNumber = 3
    wFile = 1
  elif mode == 'e':
    print('\nPlease enter the sender details: \n')
    changeSender('s')
    changeSender('p')
    changeSender('n')
    wFile = 0

  if wFile == 1:
    with open('data/sender.csv', 'r') as f:
      reader = csv.reader(f)
      for i in range(selectLineNumber):
          next(reader)
      row = next(reader)
      selectLine = row[0]

    with open('data/sender.csv','r') as f:
      lines = f.readlines()
    with open('data/sender.csv','w') as f:
      for line in lines:
        if line == selectLine + '\n':
          f.write(credential + '\n')
        else:
          f.write(line)

def updateMessage():
  #Reads the image
  with open('graph.png', 'rb') as fp:
    html_image = MIMEImage(fp.read())

  #Updates the message to be sent
  global msg
  currTime = datetime.datetime.now()
  msg = MIMEMultipart('alternative')
  msg['Subject'] = 'Temperature Alert'
  msg['From'] = email_sender_name
  msg['To'] = 'Whomever it may concern'
  html_wrap = '<html><body><p>The temperature is no longer between ' + str(threshold_max) + '°C and ' + str(threshold_min) + '°C. </p><p>The temperature is currently ' + str(temp) + '°C at ' + str(currTime.strftime("%H:%M:%S")) + '</p><p>The highest temperature reached recently is: ' + str(max_temp) + '°C at ' + str(max_temp_time) + '</p><p>The lowest temperature reached recently is: ' + str(min_temp) + '°C at ' + str(min_temp_time) + '</p><br><img alt="Temperature Graph" id="graph" src="cid:graph"></body></html>'
  msgHtml = MIMEText(html_wrap, 'html')

  #Define the image's ID
  img = open('graph.png', 'rb').read()
  msgImg = MIMEImage(img, 'png')
  msgImg.add_header('Content-ID', '<graph>')
  msgImg.add_header('Content-Disposition', 'attachment', filename='graph.png')
  msgImg.add_header('Content-Disposition', 'inline', filename='graph.png')

  msg.attach(msgHtml)
  msg.attach(msgImg)

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
      try:
        error = 0
        server.sendmail(email_sender, email_recipients[x], msg.as_string())
      except:
        print('There was an error while sending the message to ' + email_recipients[x])
        error = 1
      if error == 0:
        print('Email sent to ' + str(email_recipients[x]))
      else:
        error == 0
    print('Sent email to ' + str(len(email_recipients)) + ' addresses')
    print('Email was last sent ' + str(email_time_diff) + ' seconds ago')
    last_email_time = currTime
  else:
    print('Email was last sent ' + str(email_time_diff) + ' seconds ago')
    print('Email not sent\n')
  try:
    server.quit()
    error = 0
  except:
    print('Failed to logout')
    error = 1
  if error == 0:
    print('\nLogged out\n')

def readRecords():
  global temp
  global max_temp
  global min_temp
  global max_temp_time
  global min_temp_time

  while str(os.path.isfile('data/temp-records.csv')) == 'False':
    print('No records found')
    time.sleep(1)

  currTime = datetime.datetime.now()

  max_temp = tempreport.readCSVLine('data/temp-records.csv', 2, 'keyword', 'max', 'float')
  max_temp_time = tempreport.readCSVLine('data/temp-records.csv', 3, 'keyword', 'max')
  if float(temp) > float(max_temp):
    print('Current temp was higher than recorded max temp, updating locally\n')
    max_temp = temp
    max_temp_time = currTime.strftime("%H:%M:%S")

  min_temp = tempreport.readCSVLine('data/temp-records.csv', 2, 'keyword', 'min', 'float')
  min_temp_time = tempreport.readCSVLine('data/temp-records.csv', 3, 'keyword', 'min')
  if float(temp) < float(min_temp):
    print('Current temp was lower than recorded min temp, updating locally\n')
    min_temp = temp
    min_temp_time = currTime.strftime("%H:%M:%S")

sys.argv.append(0)
if sys.argv[1] == '-h' or sys.argv[1] == '--help':
  print('Options:')
  print('	-h  | --help           : Display the help menu')
  print('	-a  | --addresses      : Add, remove, view or edit recipient email addresses')
  print('	-p  | --password       : Update the password for the sender address used')
  print('	-s  | --sender         : Change the address of the sender email')
  print('	-n  | --name           : Change the name of the sender')
  print('	-c  | --config         : Generate a new config file')
  print('	-cs | --config-save    : Add missing config entries')
  exit()
elif sys.argv[1] == '-a' or sys.argv[1] == '--address':
  tempreport.dataEdit()
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
  tempreport.writeConfig('f')
  exit()
elif sys.argv[1] == '-cs' or sys.argv[1] == '--config-save':
  tempreport.writeConfig('s')
  exit()

print('--------------------------------')
while True:
  #Load the config
  tempreport.writeConfig('s')
  updateConfig()
  #Measure the temperature
  temp = tempreport.measureTemp()
  readRecords()
  #Update addresses and credentials
  if temp >= threshold_max or temp <= threshold_min:
    updateRecipients()
    updateSender()
    #Create message contents
    graph.generateGraph(graph_point_count)
    updateMessage()
    #Send the message
    try:
      connectToServer()
    except:
      print('There was an error while connecting to the email server')
    sendMessage()
  print('--------------------------------\n')
  time.sleep(delay)
