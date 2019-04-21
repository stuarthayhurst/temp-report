# -*- coding: utf-8 -*-
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from scipy.interpolate import make_interp_spline, BSpline
import numpy as np
import sys, argparse, re, datetime

def generateGraph(reading_count):
    kwargs={'tailmode' : True}
    args={reading_count}
    x, y  = readValues(*args, **kwargs)
    if x == '':
      print('Not enough lines in logfile, aborting\n')
      return
    drawGraph(x,y)

def drawGraph(x,y):
    x2 = mdates.date2num(x)
    x_sm = np.array(x2)
    y_sm = np.array(y)
    x_smooth = np.linspace(x_sm.min(), x_sm.max(), 200)
    spl = make_interp_spline(x2, y, k=3)
    y_smooth = spl(x_smooth)
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b-%d %H:%M'))

    plt.grid(b=True, which='major', axis='both', color='black')
    plt.plot([],[])
    x_smooth_dt = mdates.num2date(x_smooth) 
    plt.plot(x_smooth_dt, y_smooth, 'red', linewidth=1)
    plt.gcf().autofmt_xdate() 
    plt.xlabel('Time (Month-Day - Hour: Minutes)')
    plt.ylabel('Temperature \u2103')
    plt.title('Room Temperature logged by Pi')
    plt.savefig('graph.png')
    print('Created graph\n')
    plt.clf()

def readValues(*args, **kwargs):
    #for key, value in kwargs.items(): 
    #    print ("%s == %s" %(key, value))
    reading_count = args[0]
    log_dt_format = '%a %b %d %H:%M:%S %Y'
    dt_format = '%Y/%m/%d-%H:%M'
    x=[]
    y=[]
    x.clear()
    y.clear()
    try:
        tailmode = kwargs.get('tailmode')
    except:
        tailmode = True
    if not tailmode:
        from_date = kwargs.get('from_date')
        from_dt = datetime.datetime.strptime(from_date, dt_format)
        to_date = kwargs.get('to_date')
        to_dt = datetime.datetime.strptime(to_date, dt_format)
        from_dt = datetime.datetime.strptime(from_date, dt_format)
        to_dt = datetime.datetime.strptime(to_date, dt_format)
    with open('temps.log', 'r') as f:
        if tailmode:
            taildata = f.readlines() [-reading_count:]
        else:
            taildata = f.readlines()
        for line in taildata:
            data = re.split("\[(.*?)\]", line)
            if len(data) !=3: continue #ignore lines that don't have 3 elements
            temp = re.findall("[-]?\d+\.\d+", data[2]) 
            temp = float(temp[0])
            dt = datetime.datetime.strptime(data[1], log_dt_format)
            if tailmode: 
                x.append(dt)
                y.append(temp)
            else:
                if (dt >= from_dt) and (dt <= to_dt):
                    x.append(dt)
                    y.append(temp)


        return x,y

def cmd_args(args=None):
    parser = argparse.ArgumentParser("Graph.py charts range of times from a temperature log")

    parser.add_argument('-l', '--lines',  type=int, dest='reading_count', default=12,
                    help='Number of tailing log lines to plot')
    parser.add_argument('-s', '--start',  dest='start', 
                    help='Start date YYYY/MM/DD-HH:MM') 

    opt = parser.parse_args(args)

    return opt

def main(args=None):
    opt = cmd_args(args)
    #print("opt",opt)
    #print("args",args)

    #Start
    #kwargs={'tailmode': False, 'from_date' : '2019/03/29-00:00', 'to_date' : '2019/03/30-00:00' }
    
    #lines
    args = {opt.reading_count}
    kwargs={'tailmode': True}
    x, y  = readValues(*args, **kwargs) 
    drawGraph(x,y)
    sys.exit(1)

if __name__ == '__main__':
    try:
        main(sys.argv[1:])
    except ValueError:
        print("Give me something to do")
        sys.exit(1)
