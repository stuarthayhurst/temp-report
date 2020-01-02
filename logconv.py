import datetime 
import re, sys
INLOG_DT_FORMAT  = '%a %b %d %H:%M:%S %Y'
OUTLOG_DT_FORMAT = '%Y-%m-%d %H:%M:%S'
'''
Converts old templog-format
[Sun Aug 11 16:36:50 2019] Temperature: 28.19°C
to new
[2019-08-11 16:36:50] 28.19
'''

def readlog():
    with open('temps.log', 'r', encoding="utf-8") as f:
        inlog = f.readlines()
        for line in inlog:
            data = re.split("\[(.*?)\]", line)
            temp = re.findall("[-]?\d+\.\d+", data[2]) 
            dt = data[1]
            dt = date_to_dt(dt, INLOG_DT_FORMAT)
            dt = dt_to_date(dt, OUTLOG_DT_FORMAT)
            print(f'[{dt}] {temp[0]}')
        return

def date_to_dt(datestring, FORMAT):
    dateasdt = datetime.datetime.strptime(datestring, FORMAT)
    return dateasdt
 
def dt_to_date(dateasdt, FORMAT):
    datestring = datetime.datetime.strftime(dateasdt, FORMAT)
    return datestring

def main():
    readlog()

if __name__ == '__main__':
    try:
        main()
    except ValueError:
        print("Give me something to do")
        sys.exit(1)
     
