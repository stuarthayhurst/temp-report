import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import re
x=[]
y=[]

def generateGraph(reading_count_priv, time_interval_priv):
  global reading_count
  global time_interval
  print(reading_count_priv)
  reading_count = reading_count_priv
  time_interval = time_interval_priv
  x.clear()
  y.clear()
  for count in range(0, reading_count_priv):
    x.append(count * time_interval_priv)
  print('Generating graph')
  produceGraph()

def produceGraph():
  global first_run
  with open("temps.log", "r") as f:
      taildata = f.readlines() [-reading_count:]

  for line in taildata:
      data = re.findall(r"[0-9][0-9]+", line)
      y.append(int(data[4]))

  #Delete the graph

  line = plt.plot(x,y, label='Temperature °C')
  plt.xlabel('Time (Last x number of mins)')
  plt.ylabel('Temperature (°C)')
  plt.title(' Last ' + str(reading_count) + ' readings\nHot off the Pi')
  plt.legend()
  plt.savefig("graph.png")
  print('Created graph\n')
  line.cla()
