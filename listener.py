import imaplib, smtplib, datetime, time, sys, os, csv, re
import graph
from w1thermsensor import W1ThermSensor
from email.parser import HeaderParser
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

sensor = W1ThermSensor()

keywords = ['Test', 'Latest', 'Last', 'Temp', 'Temperature']
delay = 10
max_temp = 0
min_temp = 0
max_temp_time = 0
min_temp_time = 0

def updateConfig():
  while str(os.path.isfile('data/config.csv')) == 'False':
    print('No config found')
    time.sleep(10)

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
            global temp_delay
            temp_delay = int(row[1])
            config_count += 1
          elif row[0] == 'graph_point_count':
            global graph_point_count
            graph_point_count = int(row[1])
            config_count += 1
          elif row[0] == 'graph_font_path':
            global graph_font_path
            graph_font_path = str(row[1])
            config_count += 1
          elif row[0] == 'chart_type':
            global chart_type
            chart_type = str(row[1])
            config_count += 1
          line_count += 1
    print(f'Processed {config_count} config options, {line_count} lines\n')

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
      print(f'Using CSV for credentials, processed {line_count - 1} credentials, {line_count} lines')
  except FileNotFoundError:
    print('Sender credentials file not found')

def updateRecords():

  while str(os.path.isfile('data/temp-records.csv')) == 'False':
    print('No records found')
    time.sleep(1)

  with open('data/temp-records.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    config_count = 0
    line_count = 0
    for row in csv_reader:
        if line_count == 0:
          print('Reading records')
          line_count += 1
        else:
          if row[0] == 'max':
            global max_temp
            global max_temp_time
            max_temp = float(row[1])
            max_temp_time = str(row[2])
            config_count += 1
          elif row[0] == 'min':
            global min_temp
            global min_temp_time
            min_temp = float(row[1])
            min_temp_time = str(row[2])
            config_count += 1
          else:
            print('Invalid line detected\n')
          line_count += 1
    print(f'Processed {config_count} temperatures, {line_count} lines\n')


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
      global chart_type
      chart_types = ['Scatter', 'scatter', 'Line', 'line']
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
          chart_request = 0
          type_counter = 0
          while chart_request == 0 and type_counter <= len(chart_types) - 1:
            type_counter += 1
            print(type_counter)
            print(email_subject)
            i = re.findall(str(chart_types[type_counter - 1]), email_subject)
            if (i):
              chart_request = 1
              print('Graph type found\n')
              chart_type = i[0].lower()
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
  server.close()
  server.logout()
  print('Logged out\n')

def updateTemperature():
  print('Getting latest values for min and max temperature\n')
  global temp
  global max_temp
  global min_temp
  global max_temp_time
  global min_temp_time
  temp = float(sensor.get_temperature())

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
  msg['To'] = email_recipient
  html_wrap = '<html><body><p>Here is the data you requested:</p><p>The temperature is currently ' + str(temp) + '°C at ' + str(currTime.strftime("%H:%M:%S")) + '</p><p>The highest temperature reached recently is: ' + str(max_temp) + '°C at ' + str(max_temp_time) + '</p><p>The lowest temperature reached recently is: ' + str(min_temp) + '°C at ' + str(min_temp_time) + '</p><br><img alt="Temperature Graph" id="graph" src="cid:graph"></body></html>'
  wrap = MIMEText(html_wrap, 'html')

  #Define the image's ID
  html_image.add_header('Content-ID', '<graph>')
  msg.attach(html_image)
  msg.attach(wrap)

def sendMessage():
  #Use the config value for graph_point_count unless email_subject contains a command
  graph.generateGraph(graph_point_count, graph_font_path, chart_type)
  updateMessage()
  print('Sending message')
  sendServer.sendmail(email_sender, email_recipient, msg.as_string())
  print('Message sent')

counter = 0
while counter == 0:
  updateConfig()
  updateSender()
  refreshServer()
  connectToServer()
  updateRecords()
  checkMail()
  print('--------------------------------\n')
  time.sleep(delay)
