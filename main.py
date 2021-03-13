#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import re
import os
import sys
import subprocess
import json

header = """
################################################################################
                     ARRK ENGINEERING CRASH DEPARTMENT
                  JugalRasendra.Vaidya@arrk-engineering.com

    This script creates a file with all the materials (- pid)  from an inc file
    Example:  50754494 - DC04_IDS
################################################################################ """
print(header)

# read input file
input_file = sys.argv[1]
path = os.path.abspath(input_file)
out_path, include_name = os.path.split(path)
# define Text file name
if include_name.split(".")[-1] in ["inc", "inp"]:
    text_file = include_name.strip(".inc" or ".inp") + '_mat.txt'
else:
    text_file = include_name.strip(".key" or ".dyn") + '_mat.txt'
# define Animator installed path
animator_path = "animator --version 4.0.v243 -b -osm"
# read animator python session
animator_command = os.path.abspath("/proj/sim-ext/01_FGS_LSC/06_Tools/02_extern/11_matReport/Script_V3/animator_commands.py")
# read create ppt script
create_ppt = os.path.abspath("/proj/sim-ext/01_FGS_LSC/06_Tools/02_extern/11_matReport/Script_V3/create_ppt.py")
# read mad_db
with open("/proj/sim-ext/01_FGS_LSC/06_Tools/02_extern/11_matReport/Script_V3/lsd_mat_db.json") as json_data:
    mat_db_loaded = json.load(json_data)


def abq_material_list_text(input_file):
    # read inc file
    read_inc_file = open(input_file, 'r', encoding='utf-8', errors='ignore')
    # created/new file
    out_txt_path = os.path.join(out_path, text_file)
    out_txt_file = open(out_txt_path, 'w')
    start = re.compile("MATERIAL")
    filelines = read_inc_file.readlines()
    # line in new file
    line_number = 0
    word_material = "MATERIAL="
    end_material = ", "
    word_pid = "=P"
    end_pid = ";"
    # list where we put the material names
    material = []
    # list where we add the part id for the materials
    pid_list = []
    print("Info: Doing material txt file !!!")
    while line_number < len(filelines):
        if filelines[line_number][0:2] == '**' or filelines[line_number][0:2].isdigit() or filelines[line_number][0:2].isalpha() or filelines[line_number][0:2] == '\n':
            # if the line starts with ** / number / letter / or space it will skip that line
            line_number = line_number + 1
        elif start.search(filelines[line_number]):
            if word_material in filelines[line_number]:
                # generate list with material names
                material.append(filelines[line_number].split(word_material)[1].split(end_material)[0].splitlines()[0])
                # generate list with part id
                pid_list.append(int(filelines[line_number].split(word_pid)[1].split(end_pid)[0]))
                # write in new (output) file
                out_txt_file.writelines([filelines[line_number].split(word_material)[1].split(end_material)[0].splitlines()[0],
                                     ' - ', filelines[line_number].split(word_pid)[1].split(end_pid)[0]])
                out_txt_file.write("\n")
                line_number = line_number + 1
            else: 
                line_number = line_number + 1
        else:
            line_number = line_number + 1
    print("Info: Done Text file:", text_file)
    # define data
    print("Info: Doing JSON file !!!")
    data = {"include_name": include_name,
            "text_name": text_file,
            "out_path": out_path,
            "material_list": material,
            "part_list": pid_list,
            }
    # write JSON file
    with open("data.json", "w", encoding='utf-8') as outfile:
        outfile.write(json.dumps(data, indent=4, sort_keys=True, separators=(',', ': '), ensure_ascii=False))
    print("Info: Done JSON file: data.json")


def lsd_material_list_text(input_file):
    # read inc file
    read_inc_file = open(input_file, "r")
    # created/new file
    out_txt_path = os.path.join(out_path, text_file)
    out_txt_file = open(out_txt_path, 'w')
    start = re.compile("\*PART")
    filelines = [line for line in read_inc_file.readlines() if not line.startswith("$")]
    line_number = 0
    material, mid_list, pid_list, pid_name = [], [], [], []
    print("Info: Doing material txt file !!!")

    while line_number < len(filelines):
        new_line = str(filelines[line_number].strip())
        if start.search(new_line):
            pid_name.append(filelines[line_number+1].strip())
            pid = filelines[line_number+2][0:10].strip()
            mid = filelines[line_number+2][20:30].strip()
            mat_name = mat_db_loaded["{}".format(filelines[line_number + 2][20:30].strip())]
            pid_list.append(pid)
            mid_list.append(mid)
            material.append(mat_name)
            out_txt_file.writelines(str(mat_name) + " - " + str(pid))
            out_txt_file.write("\n")
            line_number = line_number + 1
        else:
            line_number = line_number+1
    print("Info: Done Text file:", text_file)
    data = {"include_name": include_name,
            "text_name": text_file,
            "out_path": out_path,
            "material_list": material,
            "part_list": pid_list,
            }
    # write JSON file
    with open("data.json", "w", encoding='utf-8') as outfile:
        outfile.write(json.dumps(data, indent=4, sort_keys=True, separators=(',', ': '), ensure_ascii=False))
    print("Info: Done JSON file: data.json")


def run_animator(options, python_script):
    print("Info: Doing Animator Task !!!")
    call_script = "%s -py %s" % (options, python_script)
    args = call_script.split()
    FNULL = open(os.devnull, "w")
    output = subprocess.Popen(args, stdout=FNULL, stderr=FNULL, bufsize=-1)
    if output.wait() != 0:
        print("Error: Animator is not closed")
    print("Info: Animator is closed !!!")
    return output


def run_ppt(python_script):
    print("Info: Doing PPT Task !!!")
    output = subprocess.call(["/share/ams/anaconda/anaconda3/RedHatEL-6/bin/python3", python_script])
    return output


if __name__ == "__main__":
    if include_name.split(".")[-1] in ["inc", "inp"]:
        abq_material_list_text(input_file)
    else:
        lsd_material_list_text(input_file)
    run_animator(options=animator_path, python_script=animator_command)
    run_ppt(python_script=create_ppt)
