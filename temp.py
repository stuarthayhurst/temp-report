import smtplib, datetime, time, csv, sys, os
import tempreport
import graph
#from w1thermsensor import W1ThermSensor
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

#Variables for email and the sensor
email_recipients = ['example@gmail.com', 'example@gmail.com'] #Set recipient emails here if use_csv_recipient = 0
email_sender = 'example@gmail.com' #Set sender email here if use_csv_sender = 0
password = 'password' #Set sender email password here if use_csv_sender = 0
last_email_time = datetime.datetime(1970, 1, 1, 0, 0)
record_reset_time = datetime.datetime(1970, 1, 1, 0, 0)
email_time_diff = 0
max_temp = -100.0
min_temp = 999.9
max_temp_time = 0
min_temp_time = 0
#sensor = W1ThermSensor()

#See data/config.csv for a config file. Use python3 temp.py -c to generate a new one

def updateConfig():
  global delay
  delay = int(tempreport.readCSVLine('data/config.csv', 1, 'keyword', 'delay'))
  global gap
  gap = int(tempreport.readCSVLine('data/config.csv', 1, 'keyword', 'gap'))
  global threshold_max
  threshold_max = float(tempreport.readCSVLine('data/config.csv', 1, 'keyword', 'threshold_max'))
  global threshold_min
  threshold_min = float(tempreport.readCSVLine('data/config.csv', 1, 'keyword', 'threshold_min'))
  global use_csv_recipient
  use_csv_recipient = int(tempreport.readCSVLine('data/config.csv', 1, 'keyword', 'use_csv_recipient'))
  global use_csv_sender
  use_csv_sender = int(tempreport.readCSVLine('data/config.csv', 1, 'keyword', 'use_csv_sender'))
  global graph_point_count
  graph_point_count = int(tempreport.readCSVLine('data/config.csv', 1, 'keyword', 'graph_point_count'))
  global record_reset
  record_reset = int(tempreport.readCSVLine('data/config.csv', 1, 'keyword', 'record_reset'))

  if delay == None:
    print('Errors occured while reading config values, attempting to fix config file:')
    tempreport.writeConfig('s')
    print('Done')
    updateConfig()

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
      removeLine = row[0]

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
        print('There was an error while sending the message')
        error = 1
      if error == 0:
        print('Message sent')
      else:
        error == 0
      print('Email sent to ' + str(email_recipients[x]))
    print('Sent email to ' + str(len(email_recipients)) + ' addresses')
    print('Email was last sent ' + str(email_time_diff) + ' seconds ago')
    last_email_time = currTime
  else:
    print('Email was last sent ' + str(email_time_diff) + ' seconds ago')
    print("Email not sent\n")
  try:
    server.quit()
    error = 0
  except:
    print("Failed to logout")
    error = 1
  if error == 0:
    print('\nLogged out\n')

def measureTemp():
  #Measures the temperature
  global temp
  print('Reading temperature:')
  temp = 30.0#float(sensor.get_temperature())
  currTime = datetime.datetime.now()
  print('The temperature is ' + str(temp) + '°C at ' + str(currTime.strftime("%H:%M:%S")) + '\n')

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

  max_temp = tempreport.readCSVLine('data/temp-records.csv', 1, 'keyword', 'max')
  max_temp_time = tempreport.readCSVLine('data/temp-records.csv', 2, 'keyword', 'max')
  if float(temp) > float(max_temp):
    print('Current temp was higher than recorded max temp, updating locally\n')
    max_temp = temp
    max_temp_time = currTime.strftime("%H:%M:%S")

  min_temp = tempreport.readCSVLine('data/temp-records.csv', 1, 'keyword', 'min')
  min_temp_time = tempreport.readCSVLine('data/temp-records.csv', 2, 'keyword', 'min')
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
  measureTemp()
  readRecords()
  #Update addresses and credentials
  if temp >= threshold_max or temp <= threshold_min:
    if use_csv_recipient == 1:
      updateRecipients()
    if use_csv_sender == 1:
      updateSender()
    #Create message contents
    graph.generateGraph(graph_point_count)
    updateMessage()
    #Send the message
    try:
      connectToServer()
    except:
      print("There was an error while connecting to the email server")
    sendMessage()
  print('--------------------------------\n')
  time.sleep(delay)
