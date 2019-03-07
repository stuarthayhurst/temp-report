import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import re
x=[0]
y=[]

def generateGraph(reading_count_priv, time_interval_priv):
  global reading_count
  global time_interval
  reading_count = reading_count_priv
  time_interval = time_interval_priv
  for count in range(1, reading_count_priv):
    x.append(count * time_interval_priv)
  produceGraph()

def produceGraph():

  with open("temps.log", "r") as f:
      taildata = f.readlines() [-reading_count:]

  for line in taildata:
      #data = re.findall(r"[\w']+", line)
      data = re.findall(r"[\w:][0-5][0-9]+", line)
      print(data)
      y.append(int(data[1]))

  plt.plot(x,y, label='Temperature °C')
  plt.xlabel('Time (Last x number of mins)')
  plt.ylabel('Temperature (°C)')
  plt.title(' Last ' + str(reading_count) + ' readings\nHot off the Pi')
  plt.legend()
  plt.savefig("graph.png")
