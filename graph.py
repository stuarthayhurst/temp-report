import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import re
x=[]
y=[]

def generateGraph(reading_count_priv, time_interval_priv):
  global reading_count
  global time_interval
  reading_count = reading_count_priv
  time_interval = time_interval_priv
  x.clear()
  y.clear()
  for count in range(0, reading_count_priv):
    x.append(count * time_interval_priv)
  print('Generating graph')
  fpath = os.path.join(rcParams["datapath"], "fonts/")
  prop = mpl.FontProperties(fname=fpath)
  fname = os.path.split(fpath)[1]
  produceGraph()

def produceGraph():
  if reading_count > len(open('temps.log').readlines(  )):
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
  from PIL import Image, ImageDraw, ImageFont
 
  img = Image.new('RGB', (100, 30), color = (73, 109, 137))
  fnt = ImageFont.truetype('/Library/Fonts/Arial.ttf', 15)
  d = ImageDraw.Draw(img)
  d.text((10,10), "Hello world", font=fnt, fill=(255, 255, 0))
  img.save('graph.png')

generateGraph(12, 5)
