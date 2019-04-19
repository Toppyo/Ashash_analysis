import pygsheets
import pandas as pd
import os
from datetime import datetime, timedelta
from tools import dataWriter, ThreadPool

save_address = '../results_anomalies/'
time_window = 7

def readCell(cell):
  ret = []
  for data in cell:
    ret.append(str(data).split('\'',1)[1].split('\'')[0])
  return ret

def readAnomalies(boundary):
    anomalies = []
    gs = pygsheets.authorize(service_file='./AnomalySheets-be83000cb032.json')
    data = gs.open('AnomalousRoutingEvents')
    sheet = data.worksheet_by_title('sheet1')
    range1 = sheet.range(boundary) #'A2:E18'
    for cell in range1:
        data = readCell(cell)
        if len(data[0])>0:
            anomalies.append([int(data[0]), data[1], data[2] if len(data[2])==8 else data[1]])
            with open("./anomalies", mode="a+") as output:
                output.write(','.join(data)+'\n')
    return anomalies

def clearAnomalies():
    try:
        os.remove("./anomalies")
    except:
        pass
    for file in os.listdir(save_address):
        try:
            os.remove(save_address+file)
        except:
            pass

def writeAnomalies(boundary, clear=True):
    if clear:
        clearAnomalies()
    anomalies = readAnomalies(boundary)
    pool = ThreadPool(4)
    tasks = []
    for anomaly in anomalies:
        print(anomaly[0])
        t1, t2 = calculateTimeWindow(anomaly[1], anomaly[2])
        print(t1)
        print(t2)
        tasks.append([anomaly[0], t1, t2, save_address])
    pool.map(writingWorker, tasks)
    pool.wait_completion()
        # dw = dataWriter(anomaly[0], t1, t2, save_address=save_address)
        # dw.main(False)

def calculateTimeWindow(t1, t2):
    return str(datetime.strptime(t1, '%Y-%m-%d')-timedelta(days=time_window))[:10],\
           str(datetime.strptime(t2, '%Y-%m-%d')+timedelta(days=time_window))[:10]

def writingWorker(params):
    dw = dataWriter(params[0], params[1], params[2], params[3])
    dw.main(False)

if __name__ == '__main__':
    writeAnomalies('A2:E12')
    # writeAnomalies('A14:E20')