#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import datetime
import re
from scipy.interpolate import spline

def drawgraph (x,y):
    x2 = mdates.date2num(x)
    x_sm = np.array(x2)
    y_sm = np.array(y)

    x_smooth = np.linspace(x_sm.min(), x_sm.max(), 200)
    y_smooth = spline(x2, y, x_smooth)

    plt.style.use('ggplot')
    plt.plot([],[])
    plt.plot(x_smooth, y_smooth, 'red', linewidth=1)
    plt.gcf().autofmt_xdate() 
    plt.ylabel("Temperature \u2103")
    plt.title('Conservatory Temperature logged by Pi')
    plt.show()

def readValues(x=[], y=[]):
    with open("temps.log", "r") as f:
        taildata = f.readlines() [-12:]
        for line in taildata:
            data = re.split("\[(.*?)\]", line)
            temp = re.findall("\d+\.\d+", data[2]) 
            temp = float(temp[0])
            dt = datetime.datetime.strptime(data[1], "%a %b %d %H:%M:%S %Y")
            x.append(dt)
            y.append(temp)
        return x,y

if __name__ == "__main__":
    x, y  = readValues()
    drawgraph(x,y)

