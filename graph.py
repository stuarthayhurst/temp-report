# -*- coding: utf-8 -*-
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from scipy.interpolate import spline
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import sys
import re, datetime, csv

plt.grid(b=None, which='major', axis='both')

def generateGraph(reading_count, font_path):
    x, y  = readValues(reading_count)
    if x == '':
      print('Not enough lines in logfile, aborting\n')
      produceText(font_path)
      return
    drawGraph(x,y)

def produceText(font_path):
    img = Image.new('RGB', (450, 40), color = (0, 0, 0))
    fnt = ImageFont.truetype(font_path, 20)
    d = ImageDraw.Draw(img)
    d.text((20,10), "Not enough lines in the log to generate a graph", font=fnt, fill=(40, 231, 35))
    img.save('graph.png')

def drawGraph(x,y):
    x2 = mdates.date2num(x)
    x_sm = np.array(x2)
    y_sm = np.array(y)

    x_smooth = np.linspace(x_sm.min(), x_sm.max(), 200)
    y_smooth = spline(x2, y, x_smooth)

    plt.style.use('ggplot')
    plt.plot([],[])
    x_smooth_dt = mdates.num2date(x_smooth) 
    plt.plot(x_smooth_dt, y_smooth, 'red', linewidth=1)
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

if __name__ == "__main__":
    reading_count = int(sys.argv[1]) if len(sys.argv) > 1 else int(12)
    x, y  = readValues(reading_count)
    drawGraph(x,y)
