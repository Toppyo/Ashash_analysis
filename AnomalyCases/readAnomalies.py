import pygsheets
import pandas as pd
import os
from datetime import datetime, timedelta
from tools import dataWriter, dataAnalyser, ThreadPool
import shutil
import numpy as np
import matplotlib.pyplot as plt

save_address = "../results_anomalies/"
fig_address = "./results_figure/"
time_window = 7
min_anomalies = 0 # 5

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
    if not os.path.exists(fig_address):
        os.mkdir(fig_address)

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

def analyzeAnomalies(params=None, plot=True):
    q = []
    pool = ThreadPool(4)
    fig_params = []
    if params is None:
        for dir in os.listdir(save_address):
            if os.path.isdir(save_address + dir):
                q.append([int(dir)])
    else:
        q = params
        fig_params = [str(x[0]) for x in params]
    pool.map(analysingWorker, q)
    pool.wait_completion()
    if plot:
        plotAnomalies(originasns=fig_params)

def plotAnomalies(originasns=[], plotBarGraph=True):
    if not os.path.exists(fig_address):
        os.mkdir(fig_address)
    if len(originasns) == 0:
        for dir in os.listdir(save_address):
            address = save_address + dir + "/"
            with open(address + "alerts", mode="r") as input:
                data = input.readlines()
            data = [x.strip().split("\n") for x in "".join(data).split("\n\n")]
            maximums = [x[:-1] for x in data]
            data = [x[-1] for x in data]
            x = [i.split(": ")[0] for i in data]
            y = [int(j.split(": ")[1]) for j in data]
            plt.figure(figsize=(10, 5))
            if plotBarGraph:
                max1st = []
                max2nd = []
                for maximum in maximums:
                    if len(maximum) == 0:
                        max1st.append(("", 0))
                        max2nd.append(("", 0))
                    elif len(maximum) == 1:
                        max1st.append((maximum[0].split(": ")[0], int(maximum[0].split(": ")[1])))
                        max2nd.append(("", 0))
                    else:
                        max1st.append((maximum[0].split(": ")[0], int(maximum[0].split(": ")[1])))
                        max2nd.append((maximum[1].split(": ")[0], int(maximum[1].split(": ")[1])))
                y2 = [x[1] for x in max1st]
                y3 = [x[1] for x in max2nd]
                plt.bar(x, y2, width=0.45, align='center', color='c', alpha=0.9)
                plt.bar(x, y3, width=0.45, bottom=y2, tick_label=y2, align='center', color='y', alpha=0.9)
                for a, b, label in zip(x, y2, [x[0] for x in max1st]):
                    if b != 0:
                        plt.text(a, b, '%s' % label, ha='center', va='bottom', fontsize=10)
                for a, b1, b2, label in zip(x, y2, y3, [x[0] for x in max2nd]):
                    if b2 != 0:
                        plt.text(a, b1 + b2 + 10, '%s' % label, ha='center', va='bottom', fontsize=10)
            plt.xticks(np.arange(len(x)), labels=x, rotation=20)
            plt.plot(x, y, 'r')
            plt.gca().set_ylim([0, ])
            # plt.savefig(address + dir)
            plt.savefig(fig_address + dir)
    else:
        for originasn in originasns:
            address = save_address + originasn + "/"
            try:
                with open(address + "alerts", mode="r") as input:
                    data = input.readlines()
            except:
                continue
            data = [x.strip().split("\n") for x in "".join(data).split("\n\n")]
            maximums = [x[:-1] for x in data]
            data = [x[-1] for x in data]
            x = [i.split(": ")[0] for i in data]
            y = [int(j.split(": ")[1]) for j in data]
            plt.figure(figsize=(10, 5))
            if plotBarGraph:
                max1st = []
                max2nd = []
                for maximum in maximums:
                    if len(maximum) == 0:
                        max1st.append(("", 0))
                        max2nd.append(("", 0))
                    elif len(maximum) == 1:
                        max1st.append((maximum[0].split(": ")[0], int(maximum[0].split(": ")[1])))
                        max2nd.append(("", 0))
                    else:
                        max1st.append((maximum[0].split(": ")[0], int(maximum[0].split(": ")[1])))
                        max2nd.append((maximum[1].split(": ")[0], int(maximum[1].split(": ")[1])))
                y2 = [x[1] for x in max1st]
                y3 = [x[1] for x in max2nd]
                plt.bar(x, y2, width=0.45, align='center', color='c', alpha=0.9)
                plt.bar(x, y3, width=0.45, bottom=y2, tick_label=y2, align='center', color='y', alpha=0.9)
                for a, b, label in zip(x, y2, [x[0] for x in max1st]):
                    if b != 0:
                        plt.text(a, b, '%s' % label, ha='center', va='bottom', fontsize=10)
                for a, b1, b2, label in zip(x, y2, y3, [x[0] for x in max2nd]):
                    if b2 != 0:
                        plt.text(a, b1 + b2 + 10, '%s' % label, ha='center', va='bottom', fontsize=10)
            plt.xticks(np.arange(12), rotation=20)
            plt.plot(x, y, 'r')
            # plt.savefig(address + originasn)
            plt.savefig(fig_address + originasn)

if __name__ == '__main__':
    # params = writeAnomalies('A2:E12', all_clear=True)
    # params = writeAnomalies('A14:E20', all_clear=False)
    # params = writeAnomalies('A8:E8')
    analyzeAnomalies()
    # plotAnomalies()