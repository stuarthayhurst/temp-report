import matplotlib.pyplot as plt
import re
x=[0,5,10,15,20,25,30,35,40,45,50,55]
y=[]

def generateGraph():

  with open("temps.log", "r") as f:
      taildata = f.readlines() [-12:]

  for line in taildata:
      data = re.findall(r"[\w']+", line)
      #x.append(int(data[0]))
      y.append(int(data[1]))

  plt.plot(x,y, label='Temperature  °C')
  plt.xlabel('Time')
  plt.ylabel('Temperature')
  plt.title(' Latest 12 readings\nHot off the Pi')
  plt.legend()
  #plt.show()
  plt.savefig("graph.png")
