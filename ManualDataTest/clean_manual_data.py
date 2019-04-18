import os

dir = "../results_manual/"
def clean():
    with open("./data_record.txt", "w+") as output:
        output.write("")
    root_dir = os.path.abspath(dir)
    files = os.listdir(root_dir)
    for file in files:
        os.remove(root_dir+"/"+file)

clean()