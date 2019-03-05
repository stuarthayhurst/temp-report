import time, csv, sys, os

#Add an argument to modify the database with data_edit.py. (Updated address_edit.py in future.)
#Add new crontab line to README.md

#Get the current list of emails in the inbox and store it in an array
#Repeatedly check for new emails by comparing the new list to the old list
#Find the outlier and get it's email address
#Check if the address matches the databse of allowed ones and send the email if it does with the current temp, min, max and timestamps. Attach the amount of emails in the inbox.
#Alert you to clear the inbox if there are 10+ emails in it.
