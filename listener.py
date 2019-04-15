import imaplib, smtplib, datetime, time, sys, os, csv, re
import tempreport
import graph
from email.parser import HeaderParser
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

keywords = ['test', 'latest', 'last', 'temp', 'temps' 'temperature', 'temperatures']
poll_rate = 10
max_temp = 0
min_temp = 0
max_temp_time = 0
min_temp_time = 0

def updateConfig():
  while str(os.path.isfile('data/config.csv')) == 'False':
    print('No config found')
    time.sleep(2)

  global delay
  delay = tempreport.readCSVLine('data/config.csv', 2, 'keyword', 'delay', 'int')
  global graph_point_count
  graph_point_count = tempreport.readCSVLine('data/config.csv', 2, 'keyword', 'graph_point_count', 'int')

  if graph_point_count == None:
    print('Errors occured while reading config values, attempting to fix config file:')
    tempreport.writeConfig('s')
    print('Done')
    updateConfig()
  print('Read config values')

def updateSender():
  global email_sender_name
  global email_sender
  global password
  if str(os.path.isfile('data/sender.csv')) == 'False':
    changeSender('e')
  email_sender      = tempreport.readCSVLine('data/sender.csv', 1, 'numbered', 2, 'str')
  password          = tempreport.readCSVLine('data/sender.csv', 1, 'numbered', 3, 'str')
  email_sender_name = tempreport.readCSVLine('data/sender.csv', 1, 'numbered', 4, 'str')

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
      #Get any available emails
      print('An email was found, saving sender address')
      header_data = data[1][0][1].decode('utf-8')
      parser = HeaderParser()
      msg = parser.parsestr(header_data)
      #Get information about the email
      email_recipient = re.search('<(.*)>', msg['From']).group(1)
      email_subject = str(msg['Subject'])
      print('Address: ' + email_recipient)
      #Check the email for keywords
      checkKeywords(email_subject, email_recipient)
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

def checkKeywords(email_subject, email_recipient):
  if any(searchstr in email_subject.lower() for searchstr in (keywords)):
    print('Keyword found\n')
    if any(searchstr in email_subject.lower() for searchstr in ('hours', 'hour')):
      print('Found request for specific time')
      hours = re.findall(r'\d+', email_subject)
      graph_point_count = int((int(hours[0]) * 60) / (delay / 60))
      print(str(hours[0]) + 'Hours, ' + str(graph_point_count) + ' points')
    graph.generateGraph(graph_point_count)
    updateMessage(email_recipient)
    sendMessage(email_recipient)

def updateMessage(email_recipient):
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

def sendMessage(email_recipient):
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
  temp = tempreport.measureTemp()
  updateRecords()
  checkMail()
  print('--------------------------------\n')
  time.sleep(poll_rate)
