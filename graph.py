# -*- coding: utf-8 -*-
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont
import re, datetime, csv

def generateGraph(reading_count, font_path, chart_type):
  x, y  = readValues(reading_count)
  if x == '':
    print('Not enough lines in logfile, aborting\n')
    produceText(font_path)
    return
  drawGraph(x,y,chart_type)

def produceText(font_path):
  img = Image.new('RGB', (450, 40), color = (0, 0, 0))
  fnt = ImageFont.truetype(font_path, 20)
  d = ImageDraw.Draw(img)
  d.text((20,10), "Not enough lines in the log to generate a graph", font=fnt, fill=(40, 231, 35))
  img.save('graph.png')

def drawGraph(x,y,chart_type):
    plt.clf()
    plt.figure()
    if chart_type == 'line':
      plt.grid(b=None, which='major', axis='both')
      plt.plot(x,y, label='Temperature in \u2103')
    elif chart_type == 'scatter':
      plt.style.use('ggplot')
      plt.plot([],[])
      plt.scatter(x,y, marker=".")
    else:
      print('Invalid config option')
    plt.gcf().autofmt_xdate() 
    plt.xlabel('Time (Day - Hour: Minutes)')
    plt.ylabel("Temperature \u2103")
    plt.title('Room Temperature logged by Pi')
    plt.savefig("graph.png")
    print('Created graph\n')
    plt.clf()

def readValues(reading_count, x=[], y=[]):
    with open("temps.log", "r") as f:
        taildata = f.readlines() [-reading_count:]
        if reading_count > len(taildata):
          return ['', '']
        for line in taildata:
            data = re.split("\[(.*?)\]", line)
            temp = re.findall("\d+\.\d+", data[2]) 
            temp = float(temp[0])
            dt = datetime.datetime.strptime(data[1], "%a %b %d %H:%M:%S %Y")
            x.append(dt)
            y.append(temp)
        return x,y
