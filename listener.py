import imaplib, smtplib, datetime, time, sys, os, csv, re
import tempreport
import graph
from email.parser import HeaderParser
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

keywords = ['test', 'latest', 'last', 'temp', 'temps' 'temperature', 'temperatures']

def updateSender():
  global email_sender_name
  global email_sender
  global password
  if os.path.isfile('data/sender.info') == False:
    csveditor.changeSender('create')
  email_sender      = str(tempreport.readCSVLine('data/sender.info', 1, 'numbered', 1))
  password          = str(tempreport.readCSVLine('data/sender.info', 1, 'numbered', 2))
  email_sender_name = str(tempreport.readCSVLine('data/sender.info', 1, 'numbered', 3))

def connectToServer():
  global servers

  #Dictionary to store mail server connections
  servers = {
    "smtp": smtplib.SMTP_SSL('smtp.gmail.com', 465),
    "imap": imaplib.IMAP4_SSL('imap.gmail.com')
  }

  #Connect to smtp server
  servers["smtp"].connect('smtp.gmail.com', 465)
  print('Connected to SMTP server')

  #Login to servers
  for protocol in ["smtp", "imap"]:
    servers[protocol].login(email_sender, password)
    print('Logged in successfully as ' + email_sender)
  print('')

def checkMail():
  global servers

  #Retrieve emails from mailserver
  server = servers["imap"]
  server.select('INBOX')
  server.search(None, 'ALL')
  data = server.fetch('1', '(BODY[HEADER])')

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

def checkKeywords(email_subject, email_recipient):
  if any(searchstr in email_subject.lower() for searchstr in (keywords)):
    print('Keyword found\n')
    if any(searchstr in email_subject.lower() for searchstr in ('hours', 'hour')):
      print('Found request for specific time')
      requested_units = re.findall(r'\d+', email_subject)
      if len(requested_units) == 0:
        requested_units = ['1']
      config.graph_point_count = int((int(requested_units[0]) * 60) / (config.log_interval / 60))
      print(str(requested_units[0]) + ' Hours, ' + str(config.graph_point_count) + ' points')
    if any(searchstr in email_subject.lower() for searchstr in ('days', 'day')):
      print('Found request for specific time')
      requested_units = re.findall(r'\d+', email_subject)
      if len(requested_units) == 0:
        requested_units = ['1']
      config.graph_point_count = int((int(requested_units[0]) * 60) / (config.log_interval / 60) * 24)
      print(str(requested_units[0]) + ' Days, ' + str(config.graph_point_count) + ' points')
    if any(searchstr in email_subject.lower() for searchstr in ('weeks', 'week')):
      print('Found request for specific time')
      requested_units = re.findall(r'\d+', email_subject)
      if len(requested_units) == 0:
        requested_units = ['1']
      config.graph_point_count = int((int(requested_units[0]) * 60) / (config.log_interval / 60) * 168)
      print(str(requested_units[0]) + ' Weeks, ' + str(config.graph_point_count) + ' points')
    graph.generateGraph(config.graph_point_count, config.area_name)
    updateMessage(email_recipient)
    sendMessage(email_recipient)

def updateMessage(email_recipient):
  #Reads the image
  with open('graph.png', 'rb') as fp:
    html_image = MIMEImage(fp.read())

  #Updates the message to be sent
  global msg
  msg = MIMEMultipart('alternative')
  msg['Subject'] = str(config.area_name) + ' Temperature Reply'
  msg['From'] = email_sender_name
  msg['To'] = email_recipient
  html_wrap = '<html><body><p>Here is the data you requested:</p><p>The temperature is currently ' + str(temp.current.value) + '°C at ' + str(datetime.datetime.now().strftime("%H:%M:%S")) + '</p><p>The highest temperature reached recently is: ' + str(temp.max.value) + '°C at ' + str(temp.max.time) + '</p><p>The lowest temperature reached recently is: ' + str(temp.min.value) + '°C at ' + str(temp.min.time) + '</p><br><img alt="Temperature Graph" id="graph" src="cid:graph"></body></html>'
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
  global servers
  print('Sending message...')
  try:
    servers["smtp"].sendmail(email_sender, email_recipient, msg.as_string())
    print('Message sent')
  except:
    print('There was an error while sending the message')

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

#Load config
while os.path.isfile('data/config.py') == False:
  time.sleep(1)
sys.path.insert(1, 'data/')
import config
print("Loaded config")

#Wait for records file
if os.path.isfile('data/temp-records.csv') == False:
  print('Waiting for record file...', end="", flush="True")
  while os.path.isfile('data/temp-records.csv') == False:
    time.sleep(1)
  print(" done\n")

#Attempt to connect to the servers
updateSender()
try:
  connectToServer()
except Exception as err:
  print('There was an error while connecting to the email server')
  print(err)
  exit(1)

try:
  while True:
    #Measure the temperature
    temp.current.value = tempreport.measureTemp()
    #Update min and max values from temp
    temp = tempreport.updateRecords(temp)
    checkMail()
    print('--------------------------------\n')
    time.sleep(config.poll_rate)
except KeyboardInterrupt:
  print(" Ctrl+C detected, logging out")
  servers["smtp"].quit()
  servers["imap"].close()
  servers["imap"].logout()
