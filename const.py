import os
import re
from pathlib import Path
from datetime import datetime

# Handin System Server Configs
HOST = '127.0.0.1'
PORT = 8000
ADDR = (HOST, PORT)

HANDINHOME = "/Users/ranya/Desktop/handin"
ROOTDIR = HANDINHOME + "/.handin"
SRCDIR = HANDINHOME + "/src"

ModCodeRE = r"^cs\d{4}$"          # UL module code re

def get_class_list_file_path(module_code):
    return os.path.join(ROOTDIR, module_code, "curr", "class-list")


def get_definitions_file_path(module_code):
    return os.path.join(ROOTDIR, module_code, "curr", "definitions.yaml")


def get_params_file_path(module_code, week_number):
    return os.path.join(ROOTDIR, module_code, "curr", "assignments", week_number, "params.yaml")


def get_vars_file_path(module_code, week_number, student_id):
    return os.path.join(ROOTDIR, module_code, "curr", student_id, week_number, "vars.yaml")


def get_program_file_path(module_code, week_number, student_id, filename_code):
    return os.path.join(ROOTDIR, module_code, "curr", "data", student_id, week_number, filename_code)

"""
Check if an /instance/ of a module exists; instance=code+"curr"
"""
def check_if_module_exists(mc: str) -> bool:
    path = os.path.join(ROOTDIR, mc, "curr")
    if os.path.exists(path):
        # modules = [name.lower() for name in os.listdir(path)]
        # if module_code.lower() in modules:
        return True
    return False


def findStudentId(stuId: str, filePath: str):
    regex = "\\b{}\\b".format(stuId)
    with open(filePath, 'r') as f:
        for line in f:
            if re.match(regex, line):
                return line
    return ''


def check_if_week_exists(module_code: str, week_number: str) -> bool:
    path = ROOTDIR, "/module/", module_code, "/", "assignments/"
    if os.path.exists(path):
        weeks = [name for name in os.listdir(path)]
        if week_number in weeks:
            return True
    return False


def check_if_ass_exists(module_code: str, ay: str, ass: str) -> bool:
    path = assPath(module_code, ay, ass)
    if os.path.exists(path):
        return True
    return False


def containsValidDay(given: str):
    names = [ r"mo(nday)?",
              r"mo|monday",
              r"tu(esday)?",
              r"we(dnesday)?",
              r"th(ursday)?",
              r"fr(iday)?",
              r"sa(turday)?",
              r"su(nday)?" ]
    for dow in names:
        if re.search(dow, given, re.IGNORECASE):
            return True
    return False


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
    return "{}/{}/{}".format(ROOTDIR, module_code.lower(), ay)


def assPath(module_code: str, ay: str, ass: str):
    return "{}/{}/{}/{}/{}".format(ROOTDIR, module_code.lower(), ay, "assignments", ass)
