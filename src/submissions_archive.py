import os
from datetime import datetime
import shutil

import const

ARCHIVE_DATE_FORMAT = "%Y-%m-%d_%H:%M:%S"

"""
    Get the top-level files, i.e. the current submission
"""
def _get_top_level_files(path) -> list:
    return [f for f in os.listdir(path) if os.path.isfile(f)]

"""
    Get the existing archives
"""
def _get_existing_archives(path) -> list:
    path = path + "/archives"
    if os.path.isdir(path):
        return [f for f in os.listdir(path) if os.path.isdir(path + "/" + f)]
    else:
        return []

"""
    This method removes all the old archives in the list that have been passed in.
    This list is returned by archive.
"""
def cull_old_archives(archives_to_cull):
    for f in archives_to_cull:
        shutil.rmtree(f)

"""
    Gets the oldest date in the list of archives
"""
def _get_oldest_date(archives):
    return min(archives)

"""
    Gets the archive file path and returning a list with any
    old archives that should be removed also
"""
def _get_archive_file_path(submission_date, path, archives):
    archives_path = path + "/archives"
    archives_cull = []
    while len(archives) >= const.ARCHIVE_NUM and const.ARCHIVE_NUM != -1:
        archives_as_dates = []
        for f in archives:
            archives_as_dates.append(datetime.strptime(f, ARCHIVE_DATE_FORMAT))

        oldest_date = _get_oldest_date(archives_as_dates)
        oldest_date = oldest_date.strftime(ARCHIVE_DATE_FORMAT)
        archives_cull.append(archives_path + "/" + oldest_date)
        archives.remove(oldest_date)

    archives_path = archives_path + "/" + submission_date

    if not os.path.isdir(archives_path):
        os.makedirs(archives_path)

    return archives_path, archives_cull

"""
    Copies the list of files to the archives path
"""
def _copy_files(top_level_path, files: list, archives_path):
    for f in files:
        path = top_level_path + "/" + f
        shutil.copy(f, archives_path + "/" + f)

"""
    Gets the submission date
"""
def _get_submission_date(top_level_path, files: list):
    for f in files:
        if f.endswith("submission-date.txt"):
            path = top_level_path + "/" + f
            with open(path, 'r') as file:
                return file.readline()

    current_date = datetime.now()
    current_date = current_date.strftime(ARCHIVE_DATE_FORMAT)

"""
    Carries out the archival process
"""
def _do_archive(path, top_level_files: list):
    archives = _get_existing_archives(path)

    submission_date = _get_submission_date(path, top_level_files)

    archives_path, old_archives = _get_archive_file_path(submission_date, path, archives)
    _copy_files(path, top_level_files, archives_path)

    return archives_path, old_archives

"""
    Archive this student's current submission if it exists.
    If const.ARCHIVE_NUM is 0, this method is a no-op

    It returns the path to the archive directory and also a list containing old
    archives to be removed as the ARCHIVE_NUM limit has been reached.

    This list allows the caller to delete the old archives when it desires,
    for example, it may only want to delete them if the submission was successful.
    (If it was unsuccessful you want to keep the last n successful submissions and not remove them)

    To remove them, pass the list into cull_old_archives
"""
def archive(student_id, module_code, ay, assignment):
    if const.ARCHIVE_NUM != 0:
        path = const.ROOTDIR + "/" + module_code + "/" + ay + "/data/" + student_id + "/" + assignment

        if os.path.isdir(path):
            files = _get_top_level_files(path)

            if (len(files) > 0):
                return _do_archive(path, files)
            return None, []
        else:
            return None, []
    else:
        return None, []
