import re
import os
import shutil
import numpy as np

save_address = "./evaluation.txt"

def evaluate():
    evaluation = {}
    results = read_results()
    shutil.copy("./data_record.txt", "./data_record_copy.txt")
    with open("./data_record_copy.txt", mode="r+") as input:
        lines = input.readlines()
    j = int(len(lines)/2)
    for i in range(j):
        print(i)
        key = lines[2*i].split("=")[1].strip()
        features = lines[2*i+1].split()
        mu = features[0].split(":")[1].strip()
        sigma = features[1].split(":")[1].strip()
        anomaly = features[2].split(":")[1].strip().strip("[").strip("]").split(",")
        label = mu+"_"+sigma
        try:
            result = results[key]
        except:
            continue
        if label in evaluation.keys():
            evaluation[label].append(recall(anomaly, result))
        else:
            evaluation[label] = [recall(anomaly, result)]
    # print(evaluation)
    write_evaluation(evaluation)
    os.remove("./data_record_copy.txt")

def read_results():
    results = {}
    result = []
    shutil.copy("./analysis.txt", "./analysis_copy.txt")
    with open("./analysis_copy.txt", mode="r+") as input:
        while True:
            line = input.readline().strip()
            if len(line) == 0:
                break
            else:
                if len(re.findall("#", line))>0:
                    key, anomaly = read_results_core(result)
                    # print(anomaly)
                    results[key] = anomaly
                    result = []
                else:
                    result.append(line)
    os.remove("./analysis_copy.txt")
    return results

def read_results_core(result):
    key = result[0].split(": ")[1].split(".")[0]
    anomaly = []
    anomaly_num = int(result[-1].split(";")[0])
    for i in range(anomaly_num):
        anomaly.append(result[-3-i])
    return key, anomaly

def recall(expectations, results):
    a = len(expectations)
    b = 0
    for result in results:
        if result in expectations:
            b += 1
            expectations.remove(result)
    return b/a

def write_evaluation(evaluation):
    with open(save_address, mode="w+") as output:
        string = ""
        for key in evaluation.keys():
            ave = np.average(evaluation[key])
            print(key + ": " + str(ave))
            string += key + ": " + str(ave) + "\n"
        output.write(string)

evaluate()