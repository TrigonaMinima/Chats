"""
Read out the FB Conversation Dumps and Make a nice log file.
You should run messages.py first.
"""

import os
import json
import datetime
import csv
# from collections import namedtuple

from config import csv_header, user_ids_final

ROOT = "FB/raw_data"


def sorted_files(dir):
    files = os.listdir(dir)
    if len(files) < 2:
        return files

    files = sorted([int(file.replace(".json", "")) for file in files])
    files = [str(file) + ".json" for file in files]

    return files


def parse_json(data, ids):
    data = data["payload"]["actions"]
    dat = {}

    for i, reply in enumerate(data):
        ts = datetime.datetime.fromtimestamp(reply["timestamp"] / 1e3)

        temp = {}
        temp["date"] = datetime.datetime.strftime(ts, "%d/%m/%Y")
        temp["time"] = datetime.datetime.strftime(ts, "%I:%M:%S %p")
        temp["name"] = ids.get(reply["author"][5:], "Group Member")
        temp["cat"] = ids.get(reply["other_user_fbid"], "Group")
        temp["data"] = reply.get("body", "")

        dat[ts] = temp

    data = []
    # for i, reply in enumerate(sorted(dat.keys())):
    #     data.append(dat[reply])

    return dat


if __name__ == "__main__":

    with open(user_ids_final, "r") as f:
        friends = [friend.strip("\n").split(",")
                   for friend in f.readlines()[1:]]
        friends = dict(friends)

    # print(dict(friends))

    for friend in os.listdir(ROOT):
        print(friend)
        files = sorted_files(os.path.join(ROOT, friend))

        csvf = ROOT.replace("raw_data", "clean_data") + "/" + friend + ".csv"

        with open(csvf, "w") as f:
            writer = csv.DictWriter(f, fieldnames=csv_header)
            writer.writeheader()

            chats = {}
            for file in files:
                data = json.load(open(os.path.join(ROOT, friend, file), "r"))
                chats.update(parse_json(data, friends))

            for chat in sorted(chats.keys()):
                writer.writerow(chats[chat])
