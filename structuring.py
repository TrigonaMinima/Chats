import os
import re


files = os.listdir("./WhatsApp/raw_data")

for file in files:
    print(file)
    with open("./WhatsApp/raw_data/" + file, "r") as f:
        lines = f.readlines()

    data = []
    for line in lines:
        if re.search(r'\d\d/\d\d/\d\d\d?\d?, \d?\d:\d\d [APap][Mm] +- +[\w ]+:', line):
            data.append(line)
        elif re.search(r'\d\d/\d\d/\d\d\d?\d?, \d?\d:\d\d [APap][Mm] +-', line):
            continue
        else:
            data[-1] = data[-1][:-1] + ". " + line

    with open("./WhatsApp/raw_data/" + file, "w") as f:
        f.writelines(data)
