#Add new crontab line to README.md

#If the subject / body has any of the keywords in it, reply with the neccessary information.
#Read in temp_delay and graph_point_count from config.
#Read in credentials from sender.csv


#Check reply by keyword.
#Add timestamp and min + max temperatures to email replies.
#Add graph to email reply.
#Save min max temp with timestamps in a seperate file and clear each restart.
#Allow asking for specific length of time. E.g. 'Last 2 hours'

import imaplib, sys, time
import graph
from email.parser import HeaderParser

temp_delay = 600#Needs to be read in from config
graph_point_count = 12#Needs to be read in from config
delay = 10

def refreshServer():
  global data
  global server
  server = imaplib.IMAP4_SSL('imap.gmail.com')
  server.login('', '')
  server.select('INBOX')
  server.search(None, 'ALL')
  data = server.fetch('1', '(BODY[HEADER])')
  print('Logged in\n')

def checkMail():
  if data[1] != [None]:
      global email_sender
      global email_subject
      print('An email was found, saving sender address')
      header_data = data[1][0][1].decode('utf-8')
      parser = HeaderParser()
      msg = parser.parsestr(header_data)
      email_sender = str(msg['From'])
      email_subject = str(msg['Subject'])
      print('Email processed, deleting email\n')
      server.store('1:*', '+X-GM-LABELS', '\\Trash')
      server.expunge()
  else:
      print('No emails\n')
  server.close()
  server.logout()
  print('Logged out')


counter = 0
while counter == 0:
  refreshServer()
  checkMail()
  graph.generateGraph(graph_point_count, temp_delay / 60)
  time.sleep(delay)
