import smtplib, datetime, time, sys, os, shutil
import commonfuncs as tempreport
import csveditor
import graph
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

#Variables for email and the sensor
email_recipients = ['']
lastEmailTime = datetime.datetime(1970, 1, 1, 0, 0)

def updateRecipients():
  global email_recipients
  if os.path.isfile('data/addresses.list') == False:
    print('\nNo address file found, starting address editor: \n')
    csveditor.dataEdit()
  print('Addresses:')
  line_count = tempreport.getLineCount('data/addresses.list')
  email_recipients = ['']
  for line in range(1, line_count):
    if line == 2:
      email_recipients[0] = str(tempreport.readCSVLine('data/addresses.list', 1, 'numbered', line))
      print(email_recipients[0])
    else:
      email_recipients.append(str(tempreport.readCSVLine('data/addresses.list', 1, 'numbered', line)))
      print(email_recipients[line - 1])

def updateSender():
  global email_sender_name
  global email_sender
  global password
  if os.path.isfile('data/sender.info') == False:
    csveditor.changeSender('create')
  email_sender      = str(tempreport.readCSVLine('data/sender.info', 1, 'numbered', 1))
  password          = str(tempreport.readCSVLine('data/sender.info', 1, 'numbered', 2))
  email_sender_name = str(tempreport.readCSVLine('data/sender.info', 1, 'numbered', 3))

def updateMessage():
  #Reads the image
  with open('graph.png', 'rb') as fp:
    html_image = MIMEImage(fp.read())

  #Updates the message to be sent
  global msg
  msg = MIMEMultipart('alternative')
  msg['Subject'] = str(config.area_name) + ' Temperature Alert'
  msg['From'] = email_sender_name
  msg['To'] = 'Whomever it may concern'
  html_wrap = '<html><body><p>The temperature is no longer between ' + str(config.threshold.max) + '°C and ' + str(config.threshold.min) + '°C. </p><p>The temperature is currently ' + str(temp.current.value) + '°C at ' + str(datetime.datetime.now().strftime("%H:%M:%S")) + '</p><p>The highest temperature reached recently is: ' + str(temp.max.value) + '°C at ' + str(temp.max.time) + '</p><p>The lowest temperature reached recently is: ' + str(temp.min.value) + '°C at ' + str(temp.min.time) + '</p><br><img alt="Temperature Graph" id="graph" src="cid:graph"></body></html>'
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
  global lastEmailTime
  #Figure out time since last email
  emailTimeDiff = (datetime.datetime.now() - lastEmailTime).total_seconds()

  #If it's been long enough since the last email, attempt to send it
  if emailTimeDiff >= config.gap:
    failedRecipients = 0
    #Loop through each recipient on the list and attempt to semd an email
    for recipient in email_recipients:
      error = 0
      try:
        server.sendmail(email_sender, recipient, msg.as_string())
      except:
        print('There was an error while sending the message to ' + recipient[x])
        error = 1
        if error == 0:
          print('Email sent to ' + str(recipient))
        else:
          failedRecipients+=1
    #Output number of emails successfully sent
    print('Sent email to ' + str(len(email_recipients) - failedRecipients) + ' addresses')
    lastEmailTime = datetime.datetime.now()
  else:
    print('Email not sent\n')

  #Only annouce when the last email was sent if it wasn't the first email
  if emailTimeDiff > config.gap * 100:
    print('Email was last sent ' + str(emailTimeDiff) + ' seconds ago')

def connectToServer():
  #Connects to gmail's servers
  global server
  server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
  server.connect('smtp.gmail.com', 465)
  print('Connected to server')
  server.login(email_sender, password)
  print('Logged in successfully as ' + email_sender + '\n')

def trySendMessage():
  try:
    sendMessage()
  except:
    print('There was an error attempting to send the email, retrying in 3 minutes')
    time.sleep(180)
    trySendMessage()

sys.argv.append(0)
if sys.argv[1] == '-h' or sys.argv[1] == '--help':
  print('Options:')
  print('	-h  | --help           : Display the help menu')
  print('	-a  | --addresses      : Add, remove, view or edit recipient email addresses')
  print('	-p  | --password       : Update the password for the sender address used')
  print('	-s  | --sender         : Change the address of the sender email')
  print('	-n  | --name           : Change the name of the sender')
  print('	-c  | --config         : Generate a new config file')
  exit()
elif sys.argv[1] == '-a' or sys.argv[1] == '--address':
  csveditor.dataEdit()
  exit()
elif sys.argv[1] == '-p' or sys.argv[1] == '--password':
  csveditor.changeSender('password')
  exit()
elif sys.argv[1] == '-s' or sys.argv[1] == '--sender':
  csveditor.changeSender('sender')
  exit()
elif sys.argv[1] == '-n' or sys.argv[1] == '--name':
  csveditor.changeSender('name')
  exit()
elif sys.argv[1] == '-c' or sys.argv[1] == '--config':
  shutil.copy2('data/config-template.py', 'data/config.py')
  exit()

print('--------------------------------')

#Create config if missing
if os.path.isfile('data/config.py') == False:
  shutil.copy2('data/config-template.py', 'data/config.py')
  print("Created missing config file")

#Load the config
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
  print('There was an error while connecting to the email server:')
  print(err)
  exit(1)

#Create temp class to store temperatures and times
temp = tempreport.returnNewTemp()

try:
  while True:
    #Measure the temperature
    temp.current.value = tempreport.measureTemp()
    #Update min and max values from temp
    temp = tempreport.updateRecords(temp)
    #Update addresses and credentials
    if temp.current.value >= config.threshold.max or temp.current.value <= config.threshold.min:
      updateRecipients()
      updateSender()
      #Create message contents
      graph.generateGraph(config.graph_point_count, config.area_name)
      updateMessage()
      #Send the message
      trySendMessage()
    print('--------------------------------\n')
    time.sleep(config.loop_delay)
except KeyboardInterrupt:
  print(" Ctrl+C detected, logging out")
  server.quit()
