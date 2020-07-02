import os
import socket
import threading
import time
from datetime import datetime

import tqdm
import yaml

import const

host = const.HANDIN_HOST
port = const.HANDIN_PORT


def get_file_content(path, mode='r'):
    with open(path, mode=mode, encoding='utf-8') as f:
        content = f.read()
    return content


def get_total_attempts(module_code, week_number) -> int:
    # read /**weekNum**/params.yaml file to get totalAttempts value
    path = const.DIR_ROOT + "/module/" + module_code + "/" + week_number + "/params.yaml"
    with open(path, 'r') as stream:
        data: dict = yaml.safe_load(stream)
    return data.get("totalAttempts")


def RetrCommand(name, sock: socket.socket):
    msg = sock.recv(1024).decode()
    print("Received command \"%s\"" % msg)

    if msg == "Authentication":
        time.sleep(.1)
        authentication_of_student(name, sock)
    elif msg == "Check attempts left":
        time.sleep(.1)
        checkAttemptsLeft(name, sock)
    elif msg == "Checking Assignment Week":
        time.sleep(.1)
        checkIfAssignmentWeek(name, sock)
    elif msg == "Check module exists":
        time.sleep(.1)
        checkIfModuleExists(name, sock)
    elif msg == "Create vars file":
        time.sleep(.1)
        createVarsFile(name, sock)
    elif msg == "Init vars file":
        time.sleep(.1)
        initVarsFile(name, sock)
    elif msg == "Check late penalty":
        time.sleep(.1)
        checkLatePenalty(name, sock)
    elif msg == "Check collection filename":
        time.sleep(.1)
        checkCollectionFilename(name, sock)
    elif msg == "Send file to server":
        time.sleep(.1)
        sendFileToServer(name, sock)
    else:
        print(f"Unknown Message: {msg}")


def authentication_of_student(name, sock):
    """check if student_id exist in the class list"""
    sock.sendall(b"OK")
    # get current module code
    module_code = sock.recv(1024).decode()
    # get student id
    student_id = sock.recv(1024).decode()
    class_list_file_path = const.get_class_list_file_path(module_code=module_code.lower())
    if os.path.exists(class_list_file_path):
        with open(class_list_file_path, 'r') as f:
            for line in f:
                if student_id in line:
                    sock.sendall(b"True")
                    print(student_id + " has been authenticated ...")
                    RetrCommand(name, sock)
                    return
    sock.sendall(b"False")
    RetrCommand(name, sock)


def checkAttemptsLeft(name, sock):
    """check number of attempts left"""
    sock.sendall(b"OK")
    module_code = sock.recv(1024).decode()
    student_id = sock.recv(1024).decode()
    week_number = sock.recv(1024).decode()
    # read vars.yaml file to get attemptsLeft value
    path = const.DIR_ROOT + "/module/" + module_code + "/data/" \
                + student_id + "/" + week_number + "/"
    filename = path + "vars.yaml"
    with open(filename, 'r') as stream:
        data: dict = yaml.safe_load(stream)
    if data.get("attemptsLeft"):
        sock.sendall(str(data.get("attemptsLeft")).encode('utf-8'))
    else:
        sock.sendall(b"False")
        print("ERROR: attemptsLeft doesn't exist!!!")
    RetrCommand(name, sock)


def checkIfModuleExists(name, sock):
    """check if the moduleCode exists"""
    sock.sendall(b"OK")
    module_code = sock.recv(1024).decode()
    path = const.DIR_ROOT + "/module/"
    if os.path.exists(path):
        modules = [name.lower() for name in os.listdir(path)]
        if module_code.lower() in modules:
            sock.sendall(b"True")
        else:
            sock.sendall(b"False")
    else:
        sock.sendall(b"False")
    RetrCommand(name, sock)


def checkIfAssignmentWeek(name, sock):
    """check if an assignment week"""
    sock.sendall(b"OK")
    module_code = sock.recv(1024).decode()
    week_number = sock.recv(1024).decode()
    path = const.DIR_ROOT + "/module/" + module_code + "/"
    if os.path.exists(path):
        weeks = [name for name in os.listdir(path)]
        if week_number in weeks:
            sock.sendall(b"True")
        else:
            sock.sendall(b"False")
    else:
        sock.sendall(b"False")
    RetrCommand(name, sock)


def createVarsFile(name, sock):
    """Create vars file for a specific student"""
    sock.sendall(b"OK")
    module_code = sock.recv(1024).decode()
    student_id = sock.recv(1024).decode()
    week_number = sock.recv(1024).decode()
    path = const.DIR_ROOT + "/module/" + module_code + "/data/" \
                + student_id + "/" + week_number + "/"
    filename = path + "vars.yaml"
    if not os.path.exists(filename):
        with open(filename, 'w'):
            pass
        sock.sendall(b"Success")
        RetrCommand(name, sock)
        return
    sock.sendall(b"Failed")
    RetrCommand(name, sock)


def initVarsFile(name, sock):
    """init vars.yaml file"""
    sock.sendall(b"OK")
    module_code = sock.recv(1024).decode()
    student_id = sock.recv(1024).decode()
    week_number = sock.recv(1024).decode()
    path = const.DIR_ROOT + "/module/" + module_code + "/data/" \
                + student_id + "/" + week_number + "/"
    filename = path + "vars.yaml"
    data = {
        "attemptsLeft": get_total_attempts(module_code, week_number),
    }
    with open(filename, 'w') as f:
        yaml.dump(data, f, default_flow_style=False)
    RetrCommand(name, sock)


def checkLatePenalty(name, sock):
    """Get late penalty"""
    sock.sendall(b"OK")
    module_code = sock.recv(1024).decode()
    week_number = sock.recv(1024).decode()

    penalty_per_day: str = getPenaltyPerDay(module_code, week_number)
    if penalty_per_day == "False":
        sock.sendall(b"ERROR: penaltyPerDay doesn't exist!!!")

    start_day: str = getStartDay(module_code, week_number)
    if start_day == "False":
        sock.sendall(b"ERROR: startDay doesn't exist!!!")

    end_day: str = getEndDay(module_code, week_number)
    if end_day == "False":
        sock.sendall(b"ERROR: endDay doesn't exist!!!")

    cutoff_day: str = getCutoffDay(module_code, week_number)
    if cutoff_day == "False":
        sock.sendall(b"ERROR: cutoffDay doesn't exist!!!")

    dt_format = "%d/%m/%Y %H:%M"
    start_day: datetime = datetime.strptime(start_day, dt_format)
    end_day: datetime = datetime.strptime(end_day, dt_format)
    cutoff_day: datetime = datetime.strptime(cutoff_day, dt_format)
    now: datetime = datetime.now()
    if now < start_day:
        sock.sendall(b"Submission to early!")
    elif now > cutoff_day:
        sock.sendall(b"You have missed the cutoff day, you are not allow to submit now!")
    elif start_day < now < end_day:
        # no late penalty applied
        sock.sendall(b"0")
    elif end_day < now < cutoff_day:
        hours_delta = (now - end_day).seconds // 3600
        sock.sendall(str((hours_delta // 24 + 1) * penalty_per_day).encode('utf-8'))
    RetrCommand(name, sock)


def checkCollectionFilename(name, sock):
    """check if the submitted filename matches the required filename"""
    sock.sendall(b"OK")
    filename = sock.recv(1024).decode()
    module_code = sock.recv(1024).decode()
    week_number = sock.recv(1024).decode()

    path = const.DIR_ROOT + "/module/" + module_code + "/" + week_number + "/"
    file = path + "params.yaml"
    with open(file, 'r') as stream:
        data = yaml.safe_load(stream)
    if data.get("collectionFilename") and str(data.get("collectionFilename")) == filename:
        sock.sendall(b"True")
    else:
        sock.sendall((str(data.get("collectionFilename")) + " is required!").encode('utf-8'))
    RetrCommand(name, sock)


def sendFileToServer(name, sock):
    """Copy code file to server side"""
    sock.sendall(b"OK")
    module_code = sock.recv(1024).decode()
    week_number = sock.recv(1024).decode()
    student_id = sock.recv(1024).decode()
    path = const.DIR_ROOT + "/module/" + module_code + "/data/" + student_id + "/" + week_number + "/"
    BUFFER_SIZE = 4096
    SEPARATOR = "<SEPARATOR>"
    filename, file_size = sock.recv(BUFFER_SIZE).decode().split(SEPARATOR)
    file_size = int(file_size)
    filename = os.path.basename(filename)
    progress = tqdm.tqdm(range(file_size), "Receiving " + filename, unit="B", unit_scale=True, unit_divisor=1024)
    with open(path + filename, 'wb') as f:
        for _ in progress:
            bytes_read = sock.recv(BUFFER_SIZE)
            if not bytes_read:
                break
            f.write(bytes_read)
            progress.update(len(bytes_read))
    RetrCommand(name, sock)


def getPenaltyPerDay(module_code, week_number):
    """get penalty per day for a module"""
    path = const.DIR_ROOT + "/module/" + module_code + "/" + week_number + "/"
    filename = path + "params.yaml"
    with open(filename, 'r') as stream:
        data = yaml.safe_load(stream)
    if data.get("penaltyPerDay"):
        return str(data.get("penaltyPerDay"))
    else:
        print("ERROR: penaltyPerDay doesn't exist!!!")
        return "False"


def getStartDay(module_code, week_number):
    """get start day for a module"""
    path = const.DIR_ROOT + "/module/" + module_code + "/" + week_number + "/"
    filename = path + "params.yaml"
    with open(filename, 'r') as stream:
        data = yaml.safe_load(stream)
    if data.get("startDay"):
        return str(data.get("startDay"))
    else:
        print("ERROR: startDay doesn't exist!!!")
        return "False"


def getEndDay(module_code, week_number):
    """get end day for a module"""
    path = const.DIR_ROOT + "/module/" + module_code + "/" + week_number + "/"
    filename = path + "params.yaml"
    with open(filename, 'r') as stream:
        data = yaml.safe_load(stream)
    if data.get("endDay"):
        return str(data.get("endDay"))
    else:
        print("ERROR: endDay doesn't exist!!!")
        return "False"


def getCutoffDay(module_code, week_number):
    """get cutoff day for a module"""
    path = const.DIR_ROOT + "/module/" + module_code + "/" + week_number + "/"
    filename = path + "params.yaml"
    with open(filename, 'r') as stream:
        data = yaml.safe_load(stream)
    if data.get("cutoffDay"):
        return str(data.get("cutoffDay"))
    else:
        print("ERROR: cutoffDay doesn't exist!!!")
        return "False"


if __name__ == '__main__':
    s = socket.socket()
    s.bind((host, port))
    s.listen(5)
    print("Server started ...")
    while True:
        c, addr = s.accept()
        print("client connected ip: <" + str(addr) + ">")
        t = threading.Thread(target=RetrCommand, args=("RetrCommand", c))
        t.start()