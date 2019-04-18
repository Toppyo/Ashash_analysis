from ihr.hegemony import Hegemony
import os
from datetime import datetime,timedelta
import shutil

save_address= './results/'

class dataWriter(object):
    def __init__(self, originasns, day1, day2, save_address=save_address):
        self.hegeDict = {}
        self.HegeDict = {}
        self.originasns = originasns
        self.startdate = day1
        self.enddate = day2
        self.save_address = save_address
        if not os.path.exists(self.save_address+'/'+str(self.originasns)):
            os.mkdir(self.save_address+'/'+str(self.originasns))
        self.save_address = self.save_address+str(self.originasns)+'/'

    def collect_main(self, clear=True):
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

# dw = dataWriter(2501, '2018-09-15', '2018-09-15')
# dw.write(False)