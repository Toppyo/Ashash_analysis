from ihr.hegemony import Hegemony
import os
from datetime import datetime,timedelta
import shutil
from threading import Thread
from queue import Queue
import numpy as np

save_address= './results/'

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
    def __init__(self, originasns, day1, day2, save_address=save_address):
        self.hegeDict = {}
        self.HegeDict = {}
        self.originasns = originasns
        self.startdate = day1
        self.enddate = day2
        self.save_address = save_address
        if not os.path.exists(self.save_address):
            os.mkdir(self.save_address)
        if not os.path.exists(self.save_address+'/'+str(self.originasns)):
            os.mkdir(self.save_address+'/'+str(self.originasns))
        self.save_address = self.save_address+str(self.originasns)+'/'

    def main(self, clear=True):
        count = 0
        if clear:
            self.clear()
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
    def __init__(self, origin_dir, originasn, add_noise=True, noise_sd=0.02):
        self.origin_dir = origin_dir + str(originasn) + "/"
        self.originasn = originasn
        self.add_noise = add_noise
        self.noise_sd = noise_sd
        self.baseline_median = {}
        self.baseline_mad = {}
        self.alertCounter = {}
        save_address = self.origin_dir + "alerts"
        self.rw = recordWriter(save_address)

    def main(self):
        for file in os.listdir(self.origin_dir):
            if file == "alerts":
                continue
            if os.path.isfile(self.origin_dir + file):
                print(file)
                # print(self.origin_dir+file)
                data = np.loadtxt(self.origin_dir+file, delimiter="\n", unpack=True)
                median, mad = self.getBaseline(data)
                key = file
                self.baseline_median[key] = median
                self.baseline_mad[key] = mad
            else:
                self.alertCounter[file] = 0
        print(self.baseline_mad)
        print(self.alertCounter)
        self.updateAlerts()
        # for date in self.alertCounter.keys():
        #     data_address = self.save_address + date + "/"


    def getBaseline(self, data):
        if self.add_noise:
            data += np.random.normal(0, self.noise_sd, len(data))
        mad = np.median(np.abs(data - np.median(data)))
        print(np.median(data))
        print(mad)
        return np.median(data), mad

    def updateAlerts(self):
        for date in self.alertCounter.keys():
            count = 0
            data_address = self.origin_dir + date + "/"
            asns = list(self.baseline_mad.keys())
            # print(self.baseline_mad.keys())
            for file in os.listdir(data_address):
                key = file
                asns.remove(file)
                # print(file)
                data = np.loadtxt(data_address+file, delimiter="\n", unpack=True)
                sub_count = sum([1 if (x > self.baseline_median[key]+3*self.baseline_mad[key]
                                       or x < self.baseline_median[key]-3*self.baseline_mad[key]) else 0 for x in data ])
                count += sub_count
                if sub_count>5:
                    self.rw.add(key.split("_")[1] + ": " + str(sub_count))
            # deal with 0*96 "invisible" file in each day
            for asn in asns:
                if 0 < self.baseline_median[asn] - self.baseline_mad[asn]*3:
                    count += 96
                    self.rw.add(asn.split("_")[1] + ": 96")
            self.rw.add(date + ": " + str(count) + "\n")
            self.alertCounter[date] = count
        self.rw.write("w+")