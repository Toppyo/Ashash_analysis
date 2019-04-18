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

from collect_data import dataWriter
import os

for file in os.listdir('./results/'):
    try:
        os.remove('./results/' + file)
    except:
        pass
save_address= './results/'
dw = dataWriter(32842, '2019-01-05', '2019-01-10', save_address)
dw.collect_main(True)

# from datetime import datetime, timedelta
#
# d1 = datetime.strptime('2018-06-24', '%Y-%m-%d')
# d2 = datetime.strptime('2018-06-25', '%Y-%m-%d')
# print(d1+timedelta(days=1)==d2)