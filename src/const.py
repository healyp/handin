import os
from pathlib import Path
from datetime import datetime

# Handin System Server Configs
HOST = '127.0.0.1'
PORT = 8000
ADDR = (HOST, PORT)

HANDINHOME = "/home/healyp/handin"
ROOTDIR = HANDINHOME + "/.handin"
SRCDIR = HANDINHOME + "/src"

def get_class_list_file_path(module_code, ay):
    return ROOTDIR + module_code + "/class-list"


def get_definitions_file_path(module_code, ay):
    return ROOTDIR + module_code + "/definitions.yaml"


def get_params_file_path(module_code, ay, week_number):
    return ROOTDIR + module_code + "/" + week_number + "/params.yaml"


def get_vars_file_path(module_code, ay, week_number, student_id):
    return ROOTDIR + module_code + "/data/" + student_id + "/" + week_number + "/vars.yaml"


def get_program_file_path(module_code, ay, week_number, student_id, filename_code):
    return ROOTDIR + module_code + "/data/" + student_id + "/" + week_number + "/" + filename_code

def whatAY():
    # datetime.today().strftime('%Y-%m-%d')
    date = datetime.today()
    startAY = date.year
    month = date.month
    sem = 1
    if (1 <= month and month <= 6):
        startAY = startAY - 1
        sem = 2
    endAY = startAY + 1

    return '{}-{}-S{}'.format(startAY, endAY, sem)

def modulePath(module_code: str, ay: str):
    return "{}/{}/{}".format(ROOTDIR, module_code.tolower(), ay)

def assPath(module_code: str, ay: str, ass: str):
    return "{}/{}/{}/{}".format(ROOTDIR, module_code.tolower(), ay, ass)
