# # import shutil
# #
# # shutil.copy("./data_record.txt", "./data_record_copy.txt")
#
#
#
# from ihr.hegemony import Hegemony
#
# # hege = Hegemony(originasns=[2501], start="2018-09-15 00:00", end="2018-09-15 23:59")
# hege = Hegemony(originasns=[2501], start="2018-09-15 00:00", end="2018-09-16 00:00")
#
# count = 1
# for r in hege.get_results():
#   print(len(r))
#   print(r)
# def readCell(cell):
#   ret = []
#   for data in cell:
#     ret.append(str(data).split('\'',1)[1].split('\'')[0])
#   return ret
#
# import pygsheets
# import pandas as pd
#
# gs = pygsheets.authorize(service_file='./AnomalySheets-be83000cb032.json')
# data = gs.open('AnomalousRoutingEvents')
# sheet = data.worksheet_by_title('sheet1')
# range1 = sheet.range('A2:E18')
# for cell in range1:
#   print(readCell(cell))

# from datetime import datetime, timedelta
#
# print(datetime(1997, int('04'), 24)+timedelta(days=1))

# from collect_data import dataWriter
# import os
#
# for file in os.listdir('./results/'):
#     try:
#         os.remove('./results/' + file)
#     except:
#         pass
# save_address= './results/'
# dw = dataWriter(32842, '2019-01-05', '2019-01-10', save_address)
# dw.collect_main(True)

# from datetime import datetime, timedelta
#
# d1 = datetime.strptime('2018-06-24', '%Y-%m-%d')
# d2 = datetime.strptime('2018-06-25', '%Y-%m-%d')
# print(d1+timedelta(days=1)==d2)

# threadingPool test#########################################
from threading import Thread
from queue import Queue

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


if __name__ == "__main__":
    from random import randrange

    save_address = "./results/"
    test_dict = {}

    def test(p1, p2):
        test_dict[p1] = p2

    keys = [str(x) for x in [randrange(3, 10) for i in range(50)]]
    vals = [randrange(2, 5) for j in range(50)]

    def combine(l1, l2):
        combined = []
        for i in range(len(l1)):
            combined.append((l1[i], l2[i]))
        return combined

    pool = ThreadPool(4)
    pool.map(test, combine(keys, vals))
    pool.wait_completion()
    print(test_dict)

    # print(combine(keys, vals))

    # Function to be executed in a thread

    # def wait_delay(d):
    #     print("sleeping for (%d)sec" % d)
    #     sleep(d)

    # Generate random delays

    # delays = [randrange(3, 7) for i in range(50)]

    # Instantiate a thread pool with 5 worker threads

    # pool = ThreadPool(5)

    # Add the jobs in bulk to the thread pool. Alternatively you could use
    # `pool.add_task` to add single jobs. The code will block here, which
    # makes it possible to cancel the thread pool with an exception when
    # the currently running batch of workers is finished.

    # pool.map(wait_delay, delays)
    # pool.wait_completion()
# threadingPool test############################################