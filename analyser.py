import os
import numpy as np
import matplotlib.pyplot as plt
from tools import recordWriter

dir = "./results_manual/"
min_mad = 0.01
recorder = recordWriter("./analysis.txt")

def ecdf(a, ax=None, **kwargs):
    sorted=np.sort( a )
    yvals=np.arange(len(sorted))/float(len(sorted))
    if ax is None:
        plt.plot( sorted, yvals, **kwargs )
    else:
        ax.plot( sorted, yvals, **kwargs )


def eccdf(a, ax=None, **kwargs):
    sorted=np.sort( a )
    yvals=np.arange(len(sorted))/float(len(sorted))
    if ax is None:
        plt.plot( sorted, 1-yvals, **kwargs )
    else:
        ax.plot( sorted, 1-yvals, **kwargs )

    return {k:v for k,v in zip(sorted, 1-yvals)}

def mad(x):
    mad = np.median(np.abs(x-np.median(x)))
    # print("mad = " + str(mad))
    # return mad if mad>0 else min_mad*np.median(x)
    # return max(0.01, mad if mad>0 else min_mad*np.median(x))
    if np.median(x)== 1:
        return  mad if mad>0 else 0.01
    # return mad if mad>0 else min_mad- min_mad*np.median(x)
    return max(mad, min_mad-min_mad*np.median(x))

def cal_ave_var(filename):
    data = np.loadtxt(filename, delimiter="\n", unpack=True)
    print("1.4826mad="+str(1.4826*mad(np.array(data))))
    recorder.add("1.4826mad="+str(1.4826*mad(np.array(data))))
    return [np.median(data), 1.4826*mad(np.array(data))]

def detectAnomaly(filename):
    count = 0
    score = []
    measured = cal_ave_var(filename)
    try:
        data = list(np.loadtxt(filename, delimiter="\n", unpack=True))
    except:
        print("Error reading: " + filename)
        recorder.add("Error reading: " + filename)
        return [0, 0., 0.]
    # if type(data) is not list:
    #     return False
    # print(data)
    lower = (measured[0] - 3*measured[1])
    upper = (measured[0] + 3*measured[1])
    # print("Median: " + str(measured[0]) + " 3*Variance: " + str(3*measured[1]))
    print(str(lower)+ " <--> " + str(upper))
    recorder.add(str(lower)+ " <--> " + str(upper))
    for val in data:
        # print(lower, upper)
        # change = found
        # found = found or (val<lower) or (val>upper)
        diff_upper = val-upper
        diff_lower = lower-val
        if diff_upper<0 and diff_lower<0:
            continue
        elif diff_upper>0:
            print(val)
            recorder.add(str(val))
            score.append(diff_upper/(3*measured[1])+1)
        elif diff_lower>0:
            print(val)
            recorder.add(str(val))
            score.append(diff_lower/(3*measured[1])+1)
        count += 1
        # change = found and not change
        # if change:
        #     print(" ".join([str(x) for x in [val, lower, upper]]))
    # return found
    return count, 0 if len(score)==0 else max(score), 0 if len(score)==0 else sum(score)/len(score)

def dict2txt(results):
    ret = ""
    for label in results.keys():
        ret += label
        ret += ": "
        ret += str(results[label][0])
        ret += " "
        ret += str(results[label][1])
        ret += "\n"
    with open("./calculations.txt", mode="w+") as output:
        output.write(ret)

def analyse(clean=False, detect=True):
    cal = {}
    root_dir = os.path.abspath(dir)
    results = os.listdir(root_dir)
    for result in results:
        key = result.split(".")[0]
        asns = key.split("_")
        print("Filename: " + result)
        recorder.add("Filename: " + result)
        if len(asns)<2 or asns[0] == asns[1]:
            # print(key)
            continue
        file = os.path.join(root_dir, result)
        cal[key] = cal_ave_var(file)
        if detect:
            # try:
            count, max, ave = detectAnomaly(file)
            if count>0:
                print("Anomaly found: " + key + "\n"
                      + str(count) + "; " + str(max) + "; " + str(ave))
                recorder.add("Anomaly found: " + key + "\n"
                      + str(count) + "; " + str(max) + "; " + str(ave))
        print("####################################################################################")
        recorder.add("####################################################################################")
                # else:
                #     print("Pass: " + key)
        # except:
            #     print("except: " + key)
            #     pass
    if clean:
        for result in results:
            file = os.path.join(root_dir, result)
            os.remove(file)

    # analysis for hegemony distributions
    # eccdf([x[1] for x in cal.values()])
    # plt.xlabel("variance")
    # plt.ylabel("CCDF")
    # plt.title("AS hegemony variance from 1002 to 1003")
    # plt.tight_layout()
    # plt.yscale("log")
    # plt.savefig("Var1002")
    # dict2txt(cal)

analyse(False, True)
recorder.write("w+")