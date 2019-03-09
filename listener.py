#Add new crontab line to README.md
#Read in temp_delay and graph_point_count from config.
#Check reply by keyword.
#Add timestamp and min + max temperatures to email replies.
#Add graph to email reply.
#Allow asking for specific length of time. E.g. 'Last 2 hours'

import imaplib, sys, time
import graph
from email.parser import HeaderParser

temp_delay = 600#Needs to be read in from config
graph_point_count = 12#Needs to be read in from config
delay = 10

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
    print('Sender credentials file not found')


def refreshServer():
  global data
  global server
  server = imaplib.IMAP4_SSL('imap.gmail.com')
  server.login(email_sender, password)
  server.select('INBOX')
  server.search(None, 'ALL')
  data = server.fetch('1', '(BODY[HEADER])')
  print('Logged in\n')

def checkMail():
  if data[1] != [None]:
      global email_subject
      #Get any available emails
      print('An email was found, saving sender address')
      header_data = data[1][0][1].decode('utf-8')
      parser = HeaderParser()
      msg = parser.parsestr(header_data)
      #Get information about the email
      email_recipient = str(msg['From'])
      email_subject = str(msg['Subject'])
      #Process the information and decide whether or not to send the email
      
      #if email_subject cointains any of the keywords
      #  send_email = 1
      #else:
      #  send_email = 0

      #Update and send the message
      if send_email = 1:
        sendMessage()
      else:
        print('Email did not contain any keywords')
      #Delete the processed email
      print('Email processed, deleting email\n')
      server.store('1:*', '+X-GM-LABELS', '\\Trash')
      server.expunge()
  else:
      print('No emails\n')
  server.close()
  server.logout()
  print('Logged out')

def updateTemperature():
  print('Getting latest values for min and max temperature:')
  global max_temp
  global min_temp
  global max_temp_time
  global min_temp_time

def updateMessage():
  updateTemperature()
  #Reads the image
  fp = open('graph.png', 'rb')
  html_image = MIMEImage(fp.read())
  fp.close()

  #Updates the message to be sent
  global msg
  currTime = datetime.datetime.now()
  msg = MIMEMultipart('alternative')
  msg['Subject'] = 'Temperature Reply'
  msg['From'] = email_sender_name
  msg['To'] = reply_sender_email
  html_wrap = '<html><body><p>Here is the data you requested:</p><p>The temperature is currently ' + str(temp) + '°C at ' + str(currTime.strftime("%H:%M:%S")) + '</p><p>The highest temperature reached recently is: ' + str(max_temp) + '°C at ' + str(max_temp_time) + '</p><br><p>The lowest temperature reached recently is: ' + str(min_temp) + '°C at ' + str(min_temp_time) + '</p><br><img alt="Temperature Graph" id="graph" src="cid:graph"></body></html>'
  wrap = MIMEText(html_wrap, 'html')

  #Define the image's ID
  html_image.add_header('Content-ID', '<graph>')
  msg.attach(html_image)
  msg.attach(wrap)

def sendMessage():
  #Use the config value for graph_point_count unless email_subject contains a command
  graph.generateGraph(graph_point_count, temp_delay / 60)
  updateMessage()
  print('Sending message')
  server.sendmail(email_sender, email_recipient, msg.as_string())
  print('Message sent')

counter = 0
while counter == 0:
  updateSender()
  refreshServer()
  checkMail()
  time.sleep(delay)
