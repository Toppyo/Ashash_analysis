import numpy as np
import random
from ManualDataTest.clean_manual_data import clean

save_address = "../results_manual/"

def create_peak(mu, sigma, anomaly):
    key = str(int(random.random()*10000))+"_"+str(int(random.random()*10000))
    label = ""
    with open(save_address+key+".txt", "w+") as output:
        print("key="+key)
        label += "key="+key+"\n"
        print("mu:" + str(mu) + " sigma:" + str(sigma) + " anomaly:[" + ",".join([str(x) for x in anomaly]) + "]")
        label += "mu:" + str(mu) + " sigma:" + str(sigma) + " anomaly:[" + ",".join([str(x) for x in anomaly]) + "]\n"
        data = list(np.random.normal(mu, sigma, 30))
        data.extend(anomaly)
        data.extend(list(np.random.normal(mu, sigma, 42-len(anomaly))))
        output.write("\n".join([str(x) for x in data]))
        with open("./data_record.txt", "a+") as output:
            output.write(label)

clean()
for i in range(1000):
    create_peak(0.3, 0.02, [0.4, 0.5, 0.6])
for i in range(1000):
    create_peak(0.3, 0.03, [0.4, 0.5, 0.6])
for i in range(1000):
    create_peak(0.2, 0.03, [0.3, 0.4, 0.5])
