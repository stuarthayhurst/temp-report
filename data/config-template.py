#Time between each loop of temp.py, in seconds (Delay between each attempt at sending an email)
loop_delay=300 #Default: 300

#Delay, in seconds, between each logged temperature measurement
log_interval=300 #Default: 300

#Minimum delay between each email sent, in seconds
gap=3600 #Default: 3600

#Time, in seconds, between each refresh of the mail box
poll_rate=10 #Default: 10

#Threshold values for minimum and maximum temperature before emailing
class threshold:
  max=30.0 #Default: 30.0
  min=-1.0 #Default: -1.0

#Number of points to plot on each graph
graph_point_count=12 #Default: 12

#Name of the area the temperature is being monitored in
area_name="Room" #Default: "Room"
