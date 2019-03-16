import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont
import re
x=[]
y=[]

def generateGraph(reading_count_priv, time_interval_priv, font_path_priv):
  global reading_count
  global time_interval
  global font_path
  reading_count = reading_count_priv
  time_interval = time_interval_priv
  font_path = font_path_priv
  x.clear()
  y.clear()
  for count in range(0, reading_count_priv):
    x.append(count * time_interval_priv)
  print('Generating graph')
  produceGraph()

def produceGraph():
  if reading_count > len(open('test.log').readlines(  )):
    print('Not enough lines in logfile, aborting\n')
    produceText()
    return

  with open("temps.log", "r") as f:
      taildata = f.readlines() [-reading_count:]

  for line in taildata:
    if re.findall(r"[0-9]+\.[0-9]+", line):
      data = re.findall(r"[0-9]+\.[0-9]+", line)
    else:
      data = re.findall(r"[0-9][0-9]+", line)
    y.append(float(data[len(data) - 1]))

  plt.plot(x,y, label='Temperature °C')
  plt.xlabel('Time (Last x number of mins)')
  plt.ylabel('Temperature (°C)')
  plt.title(' Last ' + str(reading_count) + ' readings\nHot off the Pi')
  plt.legend()
  plt.savefig("graph.png")
  print('Created graph\n')
  plt.clf()

def produceText():
  img = Image.new('RGB', (450, 40), color = (0, 0, 0))
  fnt = ImageFont.truetype(font_path, 20)
  d = ImageDraw.Draw(img)
  d.text((20,10), "Not enough lines in the log to generate a graph", font=fnt, fill=(40, 231, 35))
  img.save('graph.png')
