import os
import socket
import signal
import string
import threading
import time
import sys
from datetime import datetime
from subprocess import Popen, PIPE
import shutil
import yaml

import const

from handin_student_template import send_message, recv_message # these are the methods the handin_student script will use to communicate with this server, so import them from it
import submissions_archive

host = const.HOST
port = const.PORT

def get_file_content(path, mode='r'):
    with open(path, mode=mode, encoding='utf-8') as f:
        content = f.read()
    return content

def get_total_attempts(module_code, assignment_name) -> int:
    """read /**weekNum**/params.yaml file to get totalAttempts value"""
    path = const.get_params_file_path(module_code, assignment_name)
    with open(path, 'r') as stream:
        data: dict = yaml.safe_load(stream)
    return data.get("totalAttempts")

def getPenaltyPerDay(module_code, assignment_name):
    """get penalty per day for a module"""
    params_filepath = const.get_params_file_path(module_code, assignment_name)
    with open(params_filepath, 'r') as stream:
        data = yaml.safe_load(stream)
    if data.get("penaltyPerDay"):
        return str(data.get("penaltyPerDay"))
    else:
        print("ERROR: penaltyPerDay doesn't exist!!!")
        return "False"

def getStartDay(module_code, assignment_name):
    """get start day for a module"""
    params_filepath = const.get_params_file_path(module_code, assignment_name)
    with open(params_filepath, 'r') as stream:
        data = yaml.safe_load(stream)
    if data.get("startDay"):
        return str(data.get("startDay"))
    else:
        print("ERROR: startDay doesn't exist!!!")
        return "False"


def getEndDay(module_code, assignment_name):
    """get end day for a module"""
    params_filepath = const.get_params_file_path(module_code, assignment_name)
    with open(params_filepath, 'r') as stream:
        data = yaml.safe_load(stream)
    if data.get("endDay"):
        return str(data.get("endDay"))
    else:
        print("ERROR: endDay doesn't exist!!!")
        return "False"


def getCutoffDay(module_code, assignment_name):
    """get cutoff day for a module"""
    params_filepath = const.get_params_file_path(module_code, assignment_name)
    with open(params_filepath, 'r') as stream:
        data = yaml.safe_load(stream)
    if data.get("cutoffDay"):
        return str(data.get("cutoffDay"))
    else:
        print("ERROR: cutoffDay doesn't exist!!!")
        return "False"


def get_required_code_filename(module_code, assignment_name) -> str:
    params_path = const.get_params_file_path(module_code, assignment_name)
    with open(params_path, 'r') as stream:
        data = yaml.safe_load(stream)
    return data.get("collectionFilename") if data.get("collectionFilename") else ""


def RetrCommand(name, sock: socket.socket):
    msg = recv_message(sock)
    print("Received command \"%s\"" % msg)

    if msg == "Authentication":
        time.sleep(.1)
        authentication_of_student(name, sock)
    elif msg == "Check attempts left":
        time.sleep(.1)
        checkAttemptsLeft(name, sock)
    elif msg == "Checking Assignment Name":
        time.sleep(.1)
        checkIfAssignmentName(name, sock)
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
    elif msg == "Get exec result":
        time.sleep(.1)
        getExecResult(name, sock)
    else:
        print(f"Unknown Message: {msg}")


def authentication_of_student(name, sock):
    """check if student_id exist in the class list"""
    send_message("OK", sock)
    # get current module code
    module_code = recv_message(sock)
    # get student id
    student_id = recv_message(sock)
    class_list_file_path = const.get_class_list_file_path(module_code=module_code.lower())
    if os.path.exists(class_list_file_path):
        with open(class_list_file_path, 'r') as f:
            for line in f:
                if student_id in line:
                    send_message("True", sock)
                    print(student_id + " has been authenticated ...")
                    RetrCommand(name, sock)
                    return
    send_message("False", sock)
    RetrCommand(name, sock)


def checkAttemptsLeft(name, sock):
    """check number of attempts left"""
    send_message("OK", sock)
    module_code = recv_message(sock)
    student_id = recv_message(sock)
    assignment_name = recv_message(sock)
    # read vars.yaml file to get attemptsLeft value
    vars_filepath = const.get_vars_file_path(module_code, assignment_name, student_id)
    with open(vars_filepath, 'r') as stream:
        data: dict = yaml.safe_load(stream)
    if data.get("attemptsLeft"):
        send_message(str(data.get("attemptsLeft")), sock)
    else:
        send_message("False", sock)
        print("ERROR: attemptsLeft doesn't exist!!!")
    RetrCommand(name, sock)


def checkIfModuleExists(name, sock):
    """check if the moduleCode exists"""
    send_message("OK", sock)
    module_code = recv_message(sock)
    path = const.ROOTDIR
    if os.path.exists(path):
        modules = [name.lower() for name in os.listdir(path)]
        if module_code.lower() in modules:
            send_message("True", sock)
        else:
            send_message("False", sock)
    else:
        send_message("False", sock)
    RetrCommand(name, sock)


def checkIfAssignmentName(name, sock):
    """check if an assignment exists"""
    send_message("OK", sock)
    module_code = recv_message(sock)
    assignment_name = recv_message(sock)
    path = const.ROOTDIR + "/" + module_code + "/curr/assignments/"
    if os.path.exists(path):
        assignments = [name for name in os.listdir(path)]
        if assignment_name in assignments:
            send_message("True", sock)
        else:
            send_message("False", sock)
    else:
        send_message("False", sock)
    RetrCommand(name, sock)


def createVarsFile(name, sock):
    """Create vars file for a specific student"""
    send_message("OK", sock)
    module_code = recv_message(sock)
    student_id = recv_message(sock)
    assignment_name = recv_message(sock)
    vars_filepath = const.get_vars_file_path(module_code, assignment_name, student_id)
    vars_directory = os.path.dirname(vars_filepath)
    if not os.path.isdir(vars_directory):
        os.makedirs(vars_directory)

    if not os.path.exists(vars_filepath):
        with open(vars_filepath, 'w'):
            pass
        send_message("Success", sock)
        RetrCommand(name, sock)
        return
    send_message("Failed", sock)
    RetrCommand(name, sock)


def initVarsFile(name, sock):
    """init vars.yaml file"""
    send_message("OK", sock)
    module_code = recv_message(sock)
    student_id = recv_message(sock)
    assignment_name = recv_message(sock)
    vars_filepath = const.get_vars_file_path(module_code, assignment_name, student_id)
    params_filepath = const.get_params_file_path(module_code, assignment_name)
    with open(params_filepath, 'r') as stream:
        params: dict = yaml.safe_load(stream)

    data = {
        "attemptsLeft": get_total_attempts(module_code, assignment_name),
        "marks": 0,
    }

    if 'attendance' in params:
        data['attendance'] = 0

    if 'compilation' in params:
        data['compilation'] = 0

    with open(vars_filepath, 'w') as f:
        yaml.dump(data, f, default_flow_style=False)
    RetrCommand(name, sock)


def checkLatePenalty(name, sock):
    """Get late penalty"""
    send_message("OK", sock)
    module_code = recv_message(sock)
    assignment_name = recv_message(sock)

    penalty_per_day: str = getPenaltyPerDay(module_code, assignment_name)
    if penalty_per_day == "False":
        send_message("ERROR: penaltyPerDay doesn't exist!!!", sock)

    start_day: str = getStartDay(module_code, assignment_name)
    if start_day == "False":
        send_message("ERROR: startDay doesn't exist!!!", sock)

    end_day: str = getEndDay(module_code, assignment_name)
    if end_day == "False":
        send_message("ERROR: endDay doesn't exist!!!", sock)

    cutoff_day: str = getCutoffDay(module_code, assignment_name)
    if cutoff_day == "False":
        send_message("ERROR: cutoffDay doesn't exist!!!", sock)

    dt_format = "%Y-%m-%d %H:%M"
    start_day: datetime = datetime.strptime(start_day, dt_format)
    end_day: datetime = datetime.strptime(end_day, dt_format)
    cutoff_day: datetime = datetime.strptime(cutoff_day, dt_format)
    now: datetime = datetime.now()
    if now < start_day:
        send_message("Submission too early!", sock)
    elif now > cutoff_day:
        send_message("You have missed the cutoff day, you are not allowed to submit now!", sock)
    elif start_day < now < end_day:
        # no late penalty applied
        send_message("0", sock)
    elif end_day < now < cutoff_day:
        hours_delta = (now - end_day).seconds // 3600
        send_message(str((hours_delta // 24 + 1) * penalty_per_day), sock)
    RetrCommand(name, sock)


def checkCollectionFilename(name, sock):
    """check if the submitted filename matches the required filename"""
    send_message("OK", sock)
    filename = recv_message(sock)
    module_code = recv_message(sock)
    assignment_name = recv_message(sock)

    params_filepath = const.get_params_file_path(module_code, assignment_name)
    with open(params_filepath, 'r') as stream:
        data = yaml.safe_load(stream)
    if data.get("collectionFilename") and str(data.get("collectionFilename")) == filename:
        send_message("True", sock)
    else:
        send_message(str(data.get("collectionFilename")) + " is required!", sock)
    RetrCommand(name, sock)

archives_path = None
old_archives = []

SUBMISSION_DATE_FORMAT = "%Y-%m-%d_%H:%M:%S"

def sendFileToServer(name, sock):
    global archives_path, old_archives
    """Copy code file to server side"""
    send_message("OK", sock)
    module_code = recv_message(sock)
    assignment_name = recv_message(sock)
    student_id = recv_message(sock)
    filepath = recv_message(sock)
    filename = os.path.basename(filepath)
    path = const.get_program_file_path(module_code, assignment_name, student_id, filename)
    path_directory = os.path.dirname(path)
    if not os.path.isdir(path_directory):
        os.makedirs(path_directory)

    """
        Temporarily archive any existing submissions and if an error occurs later,
        remove the new archive and keep the existing ones.

        If no error occurs we want to cull the old_archives if we are over the
        archive limit
    """
    archives_path, old_archives = submissions_archive.archive(student_id, module_code, const.whatAY(), assignment_name)

    date_file = path_directory + "/submission-date.txt"
    current_date = datetime.now()
    current_date = current_date.strftime(SUBMISSION_DATE_FORMAT)

    with open(date_file, 'w+') as file:
        file.write(current_date)

    send_message("Start sending", sock)
    with open(path, 'wb') as f:
        while True:
            data = recv_message(sock)
            if data.endswith("DONE"):
                content, done_str = data.split("DONE")
                f.write(str(content).encode())
                break
            f.write(data)
    send_message("End sending", sock)
    RetrCommand(name, sock)

def get_file_paths(test: dict):
    input_data_file_path = test["inputDataFile"]
    if input_data_file_path != "":
        input_data_file_path = const.relativeToAbsolute(input_data_file_path)
    answer_file_path = test["answerFile"]
    if answer_file_path != "":
        answer_file_path = const.relativeToAbsolute(answer_file_path)
    filter_file_path = test["answerFile"]
    if filter_file_path != "":
        filter_file_path = const.relativeToAbsolute(test["filterFile"])

    return input_data_file_path, answer_file_path, filter_file_path

def remove_archive():
    global archives_path
    if archives_path is not None:
        shutil.rmtree(archives_path)


def getExecResult(name, sock):
    global archives_path, old_archives
    """Exec the program and get exec result"""
    send_message("OK", sock)
    module_code = recv_message(sock)
    assignment_name = recv_message(sock)
    student_id = recv_message(sock)
    file_suffix = recv_message(sock)
    penalty = recv_message(sock)

    if file_suffix == "cc" or file_suffix == "cpp":
        lang = "c++"
    elif file_suffix == "java":
        lang = "java"

    curr_marks: int = 0
    result_msg: str = ""
    required_code_filename = get_required_code_filename(module_code, assignment_name)
    code_filepath = const.get_program_file_path(module_code, assignment_name, student_id, required_code_filename)
    params_filepath = const.get_params_file_path(module_code, assignment_name)
    vars_filepath = const.get_vars_file_path(module_code, assignment_name, student_id)
    with open(params_filepath, 'r') as stream:
        data: dict = yaml.safe_load(stream)
    with open(vars_filepath, 'r') as stream:
        vars_data: dict = yaml.safe_load(stream)

    # check if attempts left
    if "attemptsLeft" in vars_data and vars_data["attemptsLeft"] > 0:
        if "tests" in data and data["tests"]:
            tests = data["tests"]
            # if attendance exists, check attendance, assign marks
            if "attendance" in tests:
                attendance = tests["attendance"]
                attendance_marks = int(attendance["marks"])
                attendance_tag = attendance["tag"]
                curr_marks = curr_marks + attendance_marks
                result_msg += "%s: %d/%d\n" % (attendance_tag, attendance_marks, attendance_marks)
                vars_data["attendance"] = attendance_marks

            compilation_succeeded = True
            # if compilation exists, check compilation, assign marks
            if "compilation" in tests:
                compilation = tests["compilation"]
                compilation_marks = int(compilation["marks"])
                compilation_tag = compilation["tag"]
                compilation_command = compilation["command"]

                # change working directory
                os.chdir(os.path.dirname(code_filepath))

                p = Popen(compilation_command, stdout=PIPE, shell=True)
                return_code = p.wait()
                if return_code == 0:
                    compilation_succeeded = True
                    # compilation successful
                    curr_marks = curr_marks + compilation_marks
                    result_msg += "%s: %d/%d\n" % (compilation_tag, compilation_marks, compilation_marks)
                    vars_data["compilation"] = compilation_marks
                else:
                    # compilation failed
                    compilation_succeeded = False
                    result_msg += "%s: %d/%d\n" % (compilation_tag, 0, compilation_marks)
                    vars_data["compilation"] = 0

                with open(vars_filepath, 'w') as f:
                    yaml.dump(vars_data, f)

            if compilation_succeeded:
                # execute the rest of custom tests when compilation success
                for key in tests.keys():
                    if key.startswith("test"):
                        test_marks = int(tests[key]["marks"])
                        test_tag = tests[key]["tag"]
                        test_command = tests[key]["command"]
                        input_data_file_path, answer_file_path, filter_file_path = get_file_paths(tests[key])
                        filter_command = tests[key]["filterCommand"]
                        stdin_input = None
                        if input_data_file_path is not None and input_data_file_path != '':
                            input_data_file = open(input_data_file_path, 'r')
                            stdin_input = input_data_file

                        # change working directory
                        os.chdir(os.path.dirname(code_filepath))
                        proc = Popen(test_command, stdin=stdin_input, stdout=PIPE, stderr=PIPE, shell=True)
                        output, stderr = proc.communicate()  # bytes

                        # compare stdout with the answer file
                        if answer_file_path is not None and answer_file_path != '':
                            answer_file = open(answer_file_path, 'rb')
                            answer: bytes = answer_file.read()

                            # use stdout and answer as two argv of filter file, then perform filtering
                            # TODO: may need to be changed ...
                            if (filter_file_path is not None and filter_file_path != '') and \
                                    (filter_command is not None and filter_command != ''):
                                try:
                                    # copy filter file to student dir
                                    filter_filename = os.path.basename(filter_file_path)
                                    filter_file_path_dst = os.path.join(os.path.dirname(code_filepath), filter_filename)
                                    with open(filter_file_path_dst, 'w'):
                                        pass
                                    shutil.copyfile(filter_file_path, filter_file_path_dst)

                                    os.chdir(os.path.dirname(filter_file_path_dst))
                                    output = replace_whitespace_with_underscore(output.decode('utf-8')).encode('utf-8')
                                    answer = replace_whitespace_with_underscore(answer.decode('utf-8')).encode('utf-8')
                                    command: str = (filter_command + " %s %s") % (output.decode('utf-8'), answer.decode('utf-8'))
                                    filter_proc = Popen(command, stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
                                    stdout, stderr = filter_proc.communicate()
                                    output, answer = stdout.decode('utf-8').split(' ')
                                except Exception as e:
                                    print(e)

                            if compare_output_with_answer(str(output), str(answer)):
                                # custom test success
                                curr_marks = curr_marks + test_marks
                                result_msg += "%s: %d/%d</br> " % (test_tag, test_marks, test_marks)
                            else:
                                # custom test failed
                                result_msg += "%s: %d/%d</br> " % (test_tag, 0, test_marks)
                                test_marks = 0

                            vars_data[key] = test_marks

            # check assignment attempts left and update attempts left
            if "attemptsLeft" in vars_data and vars_data["attemptsLeft"]:
                attemptsLeft = vars_data["attemptsLeft"]
                vars_data["attemptsLeft"] = attemptsLeft - 1
                attemptsLeft -= 1
                if attemptsLeft <= 0:
                    vars_data["attemptsLeft"] = 0
                    attemptsLeft = 0
            with open(vars_filepath, 'w') as f:
                yaml.dump(vars_data, f)
            result_msg += "</br>You have %s attempts left</br> " % str(attemptsLeft)

            # apply penalty
            curr_marks = curr_marks - int(penalty)
            result_msg += "</br>Penalty: %s</br> " % str(penalty)

            if curr_marks < 0:
                curr_marks = 0

            # update student marks
            with open(vars_filepath, 'r') as stream:
                vars_data2: dict = yaml.safe_load(stream)
            if "marks" in vars_data2.keys():
                vars_data2["marks"] = curr_marks
            with open(vars_filepath, 'w') as f:
                yaml.dump(vars_data2, f)
            result_msg += "</br>Total marks: %s</br> " % str(curr_marks)
            submissions_archive.cull_old_archives(old_archives) # this is a successful submission so, you are free to remove old ones
    else:
        result_msg = "Sorry, you have no attempts left for this assignment!"
        remove_archive() # unsuccessful submission, remove newest archive and don't remove any old ones

    archives_path = None
    old_archives = []
    send_message(result_msg, sock)
    RetrCommand(name, sock)


def compare_output_with_answer(output: str, answer: str) -> bool:
    remove = string.punctuation + string.whitespace
    return output.maketrans(dict.fromkeys(remove)) == answer.maketrans(dict.fromkeys(remove))


def replace_whitespace_with_underscore(text: str) -> str:
    return text.replace(' ', '_').replace('\r', '_').replace('\n', '_')

def signal_handler(sig, frame, sock):
    sock.close()
    sys.exit(0)

if __name__ == '__main__':
    s = socket.socket()
    s.bind((host, port))
    s.listen(5)
    signal.signal(signal.SIGINT, lambda sig, frame: signal_handler(sig, frame, s))
    print("Server started ...")
    while True:
        c, addr = s.accept()
        print("client connected ip: <" + str(addr) + ">")
        t = threading.Thread(target=RetrCommand, args=("RetrCommand", c))
        t.start()
