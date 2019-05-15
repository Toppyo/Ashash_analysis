from ihr.hegemony import Hegemony
import os
from datetime import datetime,timedelta
import shutil
from threading import Thread
from queue import Queue
import numpy as np
from operator import itemgetter
import re
import matplotlib.pyplot as plt

save_address= '/Users/sylar/work/Ashash_analysis/results/'
fig_address = '/Users/sylar/work/Ashash_analysis/results/figures/'

def sortDates(original_dates):
    dates = []
    for date in original_dates:
        date = tuple([int(x) for x in date.split("-")])
        dates.append(date)
    dates = sorted(dates, key=itemgetter(0, 1, 2))
    dates = [datetime(date[0], date[1], date[2]) for date in dates]
    dates = [str(date)[:10] for date in dates]
    return dates

def plot_roc_curve(fprs, tprs, labels, save_address=save_address):
    # plt.figure(1)
    for fpr, tpr, label in zip(fprs, tprs, labels):
        plt.plot(fpr, tpr, color=np.random.rand(3, ), label=label)
    plt.plot([0, 1], [0, 1], color='darkblue', linestyle='--')
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('Receiver Operating Characteristic (ROC) Curve')
    plt.legend()
    plt.savefig(save_address)
    plt.clf()
    plt.cla()

def plot_signals(signals, upperbound, lowerbound, xticks, save_address):
    x = np.arange(len(signals))
    plt.plot(x, signals, color='r')
    plt.plot(x, [upperbound]*len(signals), color='darkblue', linestyle='--')
    plt.plot(x, [lowerbound]*len(signals), color='darkblue', linestyle='--')
    plt.xticks([x*96+48 for x in np.arange(int(len(signals))/96)], xticks, rotation=23)
    plt.savefig(save_address)
    plt.clf()
    plt.cla()

class Worker(Thread):
    """ Thread executing tasks from a given tasks queue """
    def __init__(self, tasks):
        Thread.__init__(self)
        self.tasks = tasks
        self.daemon = True
        self.start()

    def run(self):
        while True:
            func, args, kargs = self.tasks.get()
            try:
                func(*args, **kargs)
            except Exception as e:
                # An exception happened in this thread
                print(e)
            finally:
                # Mark this task as done, whether an exception happened or not
                self.tasks.task_done()


class ThreadPool:
    """ Pool of threads consuming tasks from a queue """
    def __init__(self, num_threads):
        self.tasks = Queue(num_threads)
        for _ in range(num_threads):
            Worker(self.tasks)

    def add_task(self, func, *args, **kargs):
        """ Add a task to the queue """
        self.tasks.put((func, args, kargs))

    def map(self, func, args_list):
        """ Add a list of tasks to the queue """
        for args in args_list:
            self.add_task(func, args)

    def wait_completion(self):
        """ Wait for completion of all the tasks in the queue """
        self.tasks.join()

class dataWriter(object):
    def __init__(self, originasns, day1, day2, save_address=save_address, labeled=False, labels=[]):
        self.hegeDict = {}
        self.HegeDict = {}
        self.originasns = originasns
        self.startdate = day1
        self.enddate = day2
        self.save_address = save_address
        self.labeled = labeled
        self.labels = labels
        if not os.path.exists(self.save_address):
            os.mkdir(self.save_address)
        if not os.path.exists(self.save_address+'/'+str(self.originasns)):
            os.mkdir(self.save_address+'/'+str(self.originasns))
        self.save_address = self.save_address+str(self.originasns)+'/'

    def main(self, clear=True):
        count = 0
        if clear:
            self.clear()
        if self.labeled:
            with open(self.save_address+"labels", "w+") as output:
                output.write("\n".join([str(x) for x in self.labels]))
        d1 = datetime.strptime(self.startdate, '%Y-%m-%d')
        d2 = datetime.strptime(self.enddate, '%Y-%m-%d')+timedelta(days=1)
        while d1 != d2:
            count += 96
            self.collect(str(d1)[:10])
            d1 += timedelta(days=1)
        for key in self.HegeDict.keys():
            with open(self.save_address+key, mode='w+') as output:
                data = self.HegeDict[key]
                if len(data)<count:
                    data.extend(['0']*(count-len(data)))
                output.write('\n'.join(self.HegeDict[key])+'\n')

    def collect(self, day):
        if os.path.exists(self.save_address+day):
            print(1)
            return
        else:
            print(0)
            save_address = self.save_address+day+'/'
            os.mkdir(self.save_address+day+'/')
            hege = Hegemony(originasns=self.originasns, start=day+' 00:00', end=day+' 23:59')
            for r in hege.get_results():
                for data in r:
                    key = str(data['originasn']) + '_' + str(data['asn'])
                    if key in self.hegeDict.keys():
                        self.hegeDict[key].append(str(data['hege']))
                    else:
                        self.hegeDict[key] = [str(data['hege'])]
            self.write(save_address)

    def write(self, save_address):
        for key in self.hegeDict.keys():
            if len(self.hegeDict[key])<96:
                self.hegeDict[key].extend(['0']*(96-len(self.hegeDict[key])))
            with open(save_address+key, mode='w+') as output:
                output.write('\n'.join(self.hegeDict[key])+'\n')
        self.aggregate()

    def aggregate(self):
        for key in self.hegeDict.keys():
            if key in self.HegeDict.keys():
                self.HegeDict[key].extend(self.hegeDict[key])
            else:
                self.HegeDict[key] = self.hegeDict[key]
        self.hegeDict.clear()

    def clear(self):
        shutil.rmtree(self.save_address)
        os.mkdir(self.save_address)

class recordWriter(object):
    def __init__(self, filename):
        self.outputs = []
        self.filename = filename

    def add(self, output):
        self.outputs.append(str(output))

    def write(self, mode):
        with open(self.filename, mode=mode) as output:
            output.write("\n".join(self.outputs))

class dataAnalyser(object):
    '''
    plot_signals cant be set to True manually, please use drawSignals() in readAnomalies.py if you want to get the figures of signals
    '''
    def __init__(self, origin_dir, originasn, add_noise=True, noise_sd=0.02, start="all", end="all", min_anomalies=0, mad_param=3, plot_signals=False):
        self.origin_dir = origin_dir + str(originasn) + "/"
        self.originasn = originasn
        self.add_noise = add_noise
        self.noise_sd = noise_sd
        self.start = start
        self.end = end
        self.min_anomalies = min_anomalies
        self.mad_param = mad_param
        self.plot_signals = plot_signals
        self.baseline_median = {}
        self.baseline_mad = {}
        self.alertCounter = {}
        save_address = self.origin_dir + "alerts"
        self.rw = recordWriter(save_address)

    def main(self):
        for file in os.listdir(self.origin_dir):
            if os.path.isfile(self.origin_dir + file):
                if len(re.findall("_", file)) == 0:
                    # print(file)
                    continue
                # print(self.origin_dir+file)
                data = np.loadtxt(self.origin_dir+file, delimiter="\n", unpack=True)
                median, mad = self.getBaseline(data)
                self.baseline_median[file] = median
                self.baseline_mad[file] = mad
            else:
                if self.start is not "all":
                    if (datetime.strptime(file, '%Y-%m-%d')-datetime.strptime(self.start, '%Y-%m-%d'))/timedelta(days=1) > -1 \
                            or (datetime.strptime(file, '%Y-%m-%d')-datetime.strptime(self.end, '%Y-%m-%d'))/timedelta(days=1) < 1:
                        self.alertCounter[file] = 0
                else:
                    self.alertCounter[file] = 0
        # if self.plot_signals:
        #     for file in os.listdir(self.origin_dir):
        #         if
        # print(self.baseline_mad)
        # print(self.alertCounter)
        self.updateAlerts()
        if self.plot_signals:
            with open(self.origin_dir + "alerts", mode="r") as input:
                data = input.readlines()
            data = [x.strip().split("\n") for x in "".join(data).split("\n\n")]
            data = [x[-1] for x in data]
            ticks = [i.split(": ")[0] for i in data]
            sub_fig_address = fig_address + str(self.originasn) + "/" + ticks[0] + "_" + ticks[-1] + "/"
            if not os.path.exists(sub_fig_address):
                os.makedirs(sub_fig_address)
            for file in os.listdir(self.origin_dir):
                if os.path.isfile(self.origin_dir + file) and len(re.findall('_', file)) > 0:
                    with open(self.origin_dir + file) as input:
                        signals = [float(x.strip()) for x in input.readlines()]
                    plot_signals(signals, self.baseline_median[file]+self.mad_param*self.baseline_mad[file],
                                 self.baseline_median[file]-self.mad_param*self.baseline_mad[file], ticks, sub_fig_address+file)

    def getBaseline(self, data):
        if self.add_noise:
            data += np.random.normal(0, self.noise_sd, len(data))
        mad = np.median(np.abs(data - np.median(data)))
        # print(np.median(data))
        # print(mad)
        return np.median(data), mad

    def updateAlerts(self):
        dates = sortDates(list(self.alertCounter.keys()))
        for date in dates:
            count = 0
            data_address = self.origin_dir + date + "/"
            asns = list(self.baseline_mad.keys())
            sub_anomalies = []
            # print(self.baseline_mad.keys())
            for file in os.listdir(data_address):
                key = file
                asns.remove(file)
                # print(file)
                data = np.loadtxt(data_address+file, delimiter="\n", unpack=True)
                sub_count = sum([1 if (x > self.baseline_median[key]+self.mad_param*self.baseline_mad[key]
                                       or x < self.baseline_median[key]-self.mad_param*self.baseline_mad[key]) else 0 for x in data])
                count += sub_count
                if sub_count>self.min_anomalies:
                    # self.rw.add(key.split("_")[1] + ": " + str(sub_count))
                    sub_anomalies.append((key.split("_")[1], sub_count))
            sub_anomalies = sorted(sub_anomalies, key=lambda x: x[1], reverse=True)
            for (a, b) in sub_anomalies:
                self.rw.add(a + ": " + str(b))
            # deal with 0*96 "invisible" file in each day # TODO should we?
            # for asn in asns:
            #     if 0 < self.baseline_median[asn] - self.baseline_mad[asn]*3:
                    # count += 96
                    # self.rw.add(asn.split("_")[1] + ": 96(0)")
            self.rw.add(date + ": " + str(count) + "\n")
            self.alertCounter[date] = count
        self.rw.write("w+")

if __name__ == "__main__":
    da = dataAnalyser("./results_anomalies/", 58224)
    da.main()