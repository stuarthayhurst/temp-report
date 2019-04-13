import imaplib, smtplib, datetime, time, sys, os, csv, re
import tempreport
import graph
from w1thermsensor import W1ThermSensor
from email.parser import HeaderParser
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

keywords = ['Test', 'Latest', 'Last', 'Temp', 'Temperature']
delay = 10
max_temp = 0
min_temp = 0
max_temp_time = 0
min_temp_time = 0
sensor = W1ThermSensor()

def updateConfig():
  while str(os.path.isfile('data/config.csv')) == 'False':
    print('No config found')
    time.sleep(2)

  global delay
  delay = int(tempreport.readCSVLine('data/config.csv', 1, 'keyword', 'delay'))
  global graph_point_count
  graph_point_count = int(tempreport.readCSVLine('data/config.csv', 1, 'keyword', 'graph_point_count'))

  if delay == None:
    print('Errors occured while reading config values, attempting to fix config file:')
    tempreport.writeConfig('s')
    print('Done')
    updateConfig()

def updateSender():
  global email_sender
  global password
  global email_sender_name
  try:
    with open('data/sender.csv') as f:
      reader = csv.reader(f, delimiter=',')
      line_count = 0
      for row in reader:
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
      print(f'Using CSV for credentials, processed {line_count - 1} credentials, {line_count} lines')
  except FileNotFoundError:
    print('Sender credentials file not found')

def updateRecords():
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


def refreshServer():
  global data
  global server
  server = imaplib.IMAP4_SSL('imap.gmail.com')
  server.login(email_sender, password)
  server.select('INBOX')
  server.search(None, 'ALL')
  data = server.fetch('1', '(BODY[HEADER])')
  print('Logged in\n')

def connectToServer():
  #Connects to gmail's servers
  global sendServer
  sendServer = smtplib.SMTP_SSL('smtp.gmail.com', 465)
  sendServer.connect('smtp.gmail.com', 465)
  print('Connected to server')
  sendServer.login(email_sender, password)
  print('Logged in successfully as ' + email_sender + '\n')

def checkMail():
  if data[1] != [None]:
      global email_subject
      global email_recipient
      global extra_type
      extra_types = ['Keyword', 'Keyword', 'Keyword', 'Keyword']
      #Get any available emails
      print('An email was found, saving sender address')
      header_data = data[1][0][1].decode('utf-8')
      parser = HeaderParser()
      msg = parser.parsestr(header_data)
      #Get information about the email
      email_recipient = str(msg['From'])
      email_subject = str(msg['Subject'])
      #Process the information and decide whether or not to send the email
      email_recipient = re.split(r"[/w<]+", email_recipient)
      email_recipient = re.split(r"[/w>]+", str(email_recipient[1]))
      email_recipient = str(email_recipient[0])
      print('Address: ' + email_recipient)
      keyword = 0
      keyword_counter = 0
      while keyword == 0 and keyword_counter <= len(keywords) - 1:
        keyword_counter += 1
        x = re.findall(str(keywords[keyword_counter - 1]), email_subject)
        if (x):
          print('Keyword found\n')
          #Update and send the message
          keyword = 1
          extra_request = 0
          type_counter = 0
          while extra_request == 0 and type_counter <= len(extra_types) - 1:
            type_counter += 1
            i = re.findall(str(extra_types[type_counter - 1]), email_subject)
            if (i):
              extra_request = 1
              print('Extra type found\n')
              extra_type = i[0].lower()
            else:
              print('No graph type found')

          sendMessage()
        else:
          print('Reran')

      #Delete the processed email
      print('Email processed, deleting email\n')
      server.store('1:*', '+X-GM-LABELS', '\\Trash')
      server.expunge()
  else:
      print('No emails')
  try:
    server.close()
    server.logout()
  except:
    print('Failed to log out')
  print('Logged out\n')

def updateTemperature():
  global temp
  print('Reading current temperature\n')
  temp = float(sensor.get_temperature())

def updateMessage():
  #Reads the image
  with open('graph.png', 'rb') as fp:
    html_image = MIMEImage(fp.read())

  #Updates the message to be sent
  global msg
  currTime = datetime.datetime.now()
  msg = MIMEMultipart('alternative')
  msg['Subject'] = 'Temperature Reply'
  msg['From'] = email_sender_name
  msg['To'] = email_recipient
  html_wrap = '<html><body><p>Here is the data you requested:</p><p>The temperature is currently ' + str(temp) + '°C at ' + str(currTime.strftime("%H:%M:%S")) + '</p><p>The highest temperature reached recently is: ' + str(max_temp) + '°C at ' + str(max_temp_time) + '</p><p>The lowest temperature reached recently is: ' + str(min_temp) + '°C at ' + str(min_temp_time) + '</p><br><img alt="Temperature Graph" id="graph" src="cid:graph"></body></html>'
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
  #Use the config value for graph_point_count unless email_subject contains a command
  graph.generateGraph(graph_point_count)
  updateMessage()
  print('Sending message')
  try:
    error = 0
    sendServer.sendmail(email_sender, email_recipient, msg.as_string())
  except:
    print('There was an error while sending the message')
    error = 1
  if error == 0:
    print('Message sent')
  else:
    error == 0

while True:
  updateConfig()
  updateSender()
  try:
    refreshServer()
    connectToServer()
  except:
    print('There was an error while connecting to the email server')
  updateTemperature()
  updateRecords()
  checkMail()
  print('--------------------------------\n')
  time.sleep(delay)
