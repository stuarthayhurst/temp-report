import smtplib, time, datetime, csv, sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

#Variables for email
email_recipents = ['example@gmail.com', 'example@gmail.com'] #Set recipent emails here if use_csv_recipent = 0
email_sender = 'example@gmail.com' #Set sender email here if use_csv_sender = 0
password = 'password' #Set sender email password here if use_csv_sender = 0
last_email_time = datetime.datetime(1970, 1, 1, 0, 0)
email_time_diff = 0

#Message contents
msg = ""
#Time in seconds between each temperature reading, reccommended values:  300 - 900
delay = 6
#Minimum time in seconds between each email, reccommended values:  3600 - 7200
gap = 10
#Default temperature in degrees celcius
temp = 0
#Report temperature in degrees celcius
threshold = 30
#Toggle for using the CSV file to load addresses
use_csv_recipent = 1
#Toggle for using the CSV file to load sender information
use_csv_sender = 1

def connectToServer():
  #Connects to gmail's servers
  global server
  server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
  server.connect('smtp.gmail.com', 465)
  print('Connected to server as ' + email_sender)
  server.login(email_sender, password)
  print('Logged in successfully')
  print()

def updateRecipents():
  with open('addresses.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 0
    for row in csv_reader:
        if line_count == 0:
            print('Addresses:')
            line_count += 1
        else:
            print(f'\t{row[0]}')
            if len(email_recipents) + 1 == line_count:
              email_recipents.append(str(row[0]))
            else:
              email_recipents[line_count - 1] = str(row[0])
            line_count += 1
    print()
    print(f'Using CSV for recipent addresses, processed {line_count - 1} addresses, {line_count} lines')
    print()

def updateSender():
  global email_sender
  global password
  with open('sender.csv') as csv_file:
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
    print()
    print(f'Using CSV for credentials, processed {line_count - 1} credentials, {line_count} lines')
    print()

def changeSender():
  print('WIP')

def updateMessage():
  #Updates the message to be sent
  global msg
  msg = MIMEMultipart('alternative')
  msg['Subject'] = 'Temperature Alert'
  msg['From'] = 'Pi Temperature Alerts'
  msg['To'] = 'Whomever it may concern'
  html_wrap = '<html><body><p>The temperature has exceeded ' + str(threshold) + '°C, the temperature is currently ' + str(temp) + '°C </p></body></html>'
  wrap = MIMEText(html_wrap, 'html')

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
    for x in range(0, len(email_recipents)):
      server.sendmail(email_sender, email_recipents[x], msg.as_string())
      print('Email sent to ' + str(email_recipents[x]))
    print('Sent email to ' + str(len(email_recipents)) + ' addresses')
    print('Email was last sent ' + str(email_time_diff) + ' seconds ago')
    last_email_time = currTime
  else:
    print('Email was last sent ' + str(email_time_diff) + ' seconds ago')
    print("Email not sent")
  print()
  server.quit()

def measureTemp():
  #Measures the temperature
  global temp
  temp = 30

sys.argv.append(0)
if sys.argv[1] == '-h' or sys.argv[1] == '--help':
  print('Options:')
  print('	-h | --help    : Display the help menu')
  print('	-a | --addresses : Add, remove, view or edit recipent email addresses')
  print('	-p | --password : Change the password for the sender email')
  print('	-s | --sender : Change the address of the sender email')
  exit()
elif sys.argv[1] == '-a' or sys.argv[1] == '--address':
  import address_edit
  exit()
elif sys.argv[1] == '-p' or sys.argv[1] == '--password':
  changeSender('p')
  exit()
elif sys.argv[1] == '-s' or sys.argv[1] == '--sender':
  changeSender('s')
  exit()

print("--------------------------------")
counter = 0
while counter == 0:

  print('Reading temperature:')
  measureTemp()
  print('The temperature is ' + str(temp) + '°C')
  print()
  if temp >= threshold:
    if use_csv_recipent == 1:
      updateRecipents()
    if use_csv_sender == 1:
      updateSender()
    updateMessage()
    connectToServer()
    sendMessage()
    print("--------------------------------")
    print()
  time.sleep(delay)
