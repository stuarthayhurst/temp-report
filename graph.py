# -*- coding: utf-8 -*-
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from scipy.interpolate import make_interp_spline, BSpline
import numpy as np
import sys, argparse, re, datetime

DT_FORMAT       = '%Y/%m/%d-%H:%M'
LOG_DT_FORMAT   = '%a %b %d %H:%M:%S %Y'

def generateGraph(reading_count):
    '''Wrapper for drawgraph called from '''
    kwargs = {'tailmode' : True}
    args   = {reading_count}
    x, y   = readValues(*args, **kwargs)
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
    for key, value in kwargs.items():     #Debug
        print ("%s == %s" %(key, value)) #Debug

    if kwargs.get('lines') != None:
        reading_count = kwargs.get('lines')
    else:
        reading_count = args[0]

    log_dt_format = '%a %b %d %H:%M:%S %Y'

    x=[]
    y=[]
    x.clear()
    y.clear()
    try:
        tailmode = kwargs.get('tailmode')
    except:
        tailmode = True
    if not tailmode:
        from_dt = date_to_dt(kwargs.get('from_date'),DT_FORMAT)
        to_dt = date_to_dt(kwargs.get('to_date'),DT_FORMAT)

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
            dt = date_to_dt(data[1], LOG_DT_FORMAT)
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

    parser.add_argument('-l', '--lines',  type=int, dest='lines', default=12,
                    help='Number of tailing log lines to plot')
    parser.add_argument('-s', '--start',  dest='start',
                    help='Start date YYYY/MM/DD-HH:MM')
    parser.add_argument('-e', '--end',  dest='end',
                    help='End   date YYYY/MM/DD-HH:MM')
    parser.add_argument('-d', '--dur',  dest='dur',
                    help='Duration: Hours, Days, Weeks, Months e.g. 2W for 2 weeks')

    opt = parser.parse_args(args)

    return opt

def parse_duration(duration):
    print("Duration == ",duration)
    #duration_delta = datetime.datetime.timedelta(days=7)
    return duration_delta.datetime.datetime.strftime("%d/%m/%Y")

def date_to_dt(datestring, FORMAT):
    dateasdt = datetime.datetime.strptime(datestring, FORMAT)
    return dateasdt

def main(args=None):
    opt = cmd_args(args)
    kwargs = {}

    if opt.dur and opt.start and opt.end: #Assume Start and range ignore end //TODO//
        print("all three madness") #Debug
        opt.end_dt = date_to_dt(opt.start, DT_FORMAT)+datetime.timedelta(days=7)
        opt.end = opt.end_dt.strftime(DT_FORMAT)
        kwargs={'tailmode': False, 'from_date': opt.start, 'to_date': opt.end, **kwargs}

    if opt.dur and opt.start and not opt.end: #Start and range //TODO- parseduration call//
        print("Start & Duration") #Debug
        opt.end_dt = date_to_dt(opt.start, DT_FORMAT)+datetime.timedelta(days=7)
        opt.end = opt.end_dt.strftime(DT_FORMAT)
        kwargs={'tailmode': False, 'from_date': opt.start, 'to_date': opt.end, **kwargs}

    if opt.dur and not opt.start and opt.end: #Range before enddate //TODO//
        print("End and Duration") #Debug
        
    if opt.dur and not opt.start and not opt.end: #tailmode with range //TODO//
        print("call from end back to duratiion") #Debug

    if not opt.dur and opt.start and opt.end: #Date range
        kwargs={'tailmode': False, 'from_date': opt.start, 'to_date': opt.end, **kwargs}

    if not opt.dur and not opt.start and not opt.end: #tailmode with lines
        kwargs={'tailmode': True, 'lines': opt.lines, **kwargs}

    x, y  = readValues(*args, **kwargs)
    drawGraph(x,y)
    sys.exit(1)

if __name__ == '__main__':
    try:
        main(sys.argv[1:])
    except ValueError:
        print("Give me something to do")
        sys.exit(1)
