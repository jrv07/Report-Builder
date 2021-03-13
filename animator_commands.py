import gnspy
import os
from collections import defaultdict
import json

# global varibales

with open("data.json") as json_data:
    data_loaded = json.load(json_data)
    # print(data_loaded)
    include_name = data_loaded["include_name"]
    out_path = data_loaded["out_path"]
    text_name = data_loaded["text_name"]
    inc_path = os.path.join(out_path, include_name)

if include_name.split(".")[-1] in ["inc", "inp"]:
    interface_name = "Abaqus_auto"
else:
    interface_name = "Dyna3d"

# animator variables
a4 = gnspy.a4
allslots = a4.getSlotList()
slot = allslots[0]
allviews = a4.getViewList()
view = allviews[0]


def animator_start(interface_name):
    interface = interface_name
    a4.executeCommand("rea fil {} {} GEO=0:pid:all ADD=no".format(interface, inc_path), slot)
    a4.executeCommand("col bac white", slot, view)
    a4.executeCommand("col ove black", slot, view)


def animator_groups(out_path, include_name):
    filename = text_name
    file_path = os.path.join(out_path, filename)
    readfile = open(file_path, "r")
    file_lines = readfile.readlines()
    line_number = 0
    data, pids, mids, animator_groups, temp = [], [], [], [], []
    while line_number < len(file_lines):
        data.append(file_lines[line_number].strip().split(" - "))
        mids.append(data[line_number][0])
        pids.append(int(data[line_number][1]))
        line_number = line_number + 1
    data = list(zip(mids, pids))
    output = defaultdict(list)
    for key, val in data:
        output[key].append(val)
    # create animator groups
    for x, y in output.items():
        a4.executeCommand("era all", slot, view)
        for j in y:
            a4.executeCommand("add pid %s" % j, slot, view)
        a4.executeCommand("gro def %s" % x, slot, view)
    # create animator pictures
    for k, v in output.items():
        a4.executeCommand("add all", slot, view)
        a4.executeCommand("era pid -99999999-0", slot, view)
        a4.executeCommand("col pid gray30 all", slot, view)
        a4.executeCommand("col mtt 0.1 all", slot, view)
        a4.executeCommand("col pid orange gro %s" % k, slot, view)
        a4.executeCommand("txt del all", slot, view)
        a4.executeCommand('txt scr add 0.2 0.95 "MAT = {}"'.format(k, slot, view))
        a4.executeCommand("txt scr mod col for orange all", slot, view)
        a4.executeCommand("txt scr mod fon fam Arial all", slot, view)
        a4.executeCommand("xcm ghe 800", slot, view)
        a4.executeCommand("xcm gwi 800", slot, view)
        a4.executeCommand("vie cen", slot, view)
        a4.executeCommand("vie sca 0.9", slot, view)
        a4.executeCommand("wri png {}/%s.png".format(out_path) % k, slot, view)


def animator_close():
    a4.executeCommand("bye", slot, view)


animator_start(interface_name=interface_name)
animator_groups(out_path=out_path, include_name=include_name)
animator_close()

