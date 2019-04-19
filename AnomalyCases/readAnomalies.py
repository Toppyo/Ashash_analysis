import pygsheets
import pandas as pd
import os
from datetime import datetime, timedelta
from tools import dataWriter, dataAnalyser, ThreadPool
import shutil

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

def clearAnomalies(deep=False):
    try:
        os.remove("./anomalies")
    except:
        pass
    if deep:
        shutil.rmtree(save_address)
        os.mkdir(save_address)
    else:
        for dir in os.listdir(save_address):
            address = save_address + dir +"/"
            for file in address:
                if os.path.isfile(file):
                    os.remove(file)

def writeAnomalies(boundary, all_clear=False):
    ret = []
    clearAnomalies(all_clear)
    anomalies = readAnomalies(boundary)
    pool = ThreadPool(4)
    tasks = []
    for anomaly in anomalies:
        print(anomaly[0])
        t1, t2 = calculateTimeWindow(anomaly[1], anomaly[2])
        print(t1)
        print(t2)
        ret.append([anomaly[0], t1, t2])
        tasks.append([anomaly[0], t1, t2, save_address])
    pool.map(writingWorker, tasks)
    pool.wait_completion()
    return ret
        # dw = dataWriter(anomaly[0], t1, t2, save_address=save_address)
        # dw.main(False)

# F for forward, N for normal
def calculateTimeWindow(t1, t2, mode='F'):
    if mode=='N':
        return str(datetime.strptime(t1, '%Y-%m-%d')-timedelta(days=time_window))[:10],\
               str(datetime.strptime(t2, '%Y-%m-%d')+timedelta(days=time_window))[:10]
    if mode=='F':
        return str(datetime.strptime(t1, '%Y-%m-%d')-2*timedelta(days=time_window))[:10], t2

def writingWorker(params):
    dataWriter(params[0], params[1], params[2], params[3]).main(False)

def analysingWorker(params):
    if len(params)==1:
        dataAnalyser(origin_dir=save_address, originasn=params[0]).main()
    else:
        dataAnalyser(origin_dir=save_address, originasn=params[0], start=params[1], end=params[2]).main()

def analyzeAnomalies(params=None):
    q = []
    pool = ThreadPool(4)
    if params is None:
        for dir in os.listdir(save_address):
            if os.path.isdir(save_address + dir):
                q.append(int(dir))
    else:
        q = params
    pool.map(analysingWorker, q)
    pool.wait_completion()

if __name__ == '__main__':
    # params = writeAnomalies('A2:E12', all_clear=True)
    params = writeAnomalies('A14:E20', all_clear=False)
    analyzeAnomalies(params=params)