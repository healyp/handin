"""
    This file provides methods for using definitions to calculate start, end and cutoff days
    and other utility methods if needed
"""

import re
import datetime

FORMAT_REGEX = r"^(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)[,]\s%w([+-][0-9]+){0,1}(\s%t[0-9]{2}:[0-9]{2}){0,1}$"
LONG_WEEK_REGEX = r"^week[0-9]{1,2}$"
SHORT_WEEK_REGEX = r"^w[0-9]{1,2}$"
DATE_FORMAT = "%Y-%m-%d"

WEEK_DAYS = {
    "Monday": 0,
    "Tuesday": 1,
    "Wednesday": 2,
    "Thursday": 3,
    "Friday": 4,
    "Saturday": 5,
    "Sunday": 6
}

"""
    Represents a string of a week definition parsed in.
    Day represents the day string, week_number represents the calculated week
    number based off the week placeholder, hour and minutes represents time passed
    in. (If not passed in, it defaults to 23:59)

    E.g. Monday, %w+1 %t16:30
    With w01 passed in, Monday is passed in as day, %w+1 becomes 2. hours becomes 16
    and minutes becomes 30

    %tHH:MM can be left out as the _parse_week_number defaults it to 23:59
"""
class ParsedDefinitionsDate:
    def __init__(self, day, week_number, hours, minutes):
        self.day = day
        self.week_number = week_number
        self.hours = hours
        self.minutes = minutes

def _add_weeks(date, num_weeks):
    date = datetime.datetime.strptime(date, DATE_FORMAT)
    delta = datetime.timedelta(days=7 * num_weeks)
    return date + delta

def _get_date_of_day(date, day, hours=23, minutes=59):
    day_num = WEEK_DAYS[day]
    delta = datetime.timedelta(days=day_num)
    return (date + delta).replace(hour=hours, minute=minutes)

"""
    Normalizes the provided week_number to a wxx in case it is in the format
    week01.

    For example, if the week number is given as Week01, it will be normalized to w01
"""
def normalize_week_number(week_number):
    week_number = week_number.lower()
    longWeek = re.compile(LONG_WEEK_REGEX)
    shortWeek = re.compile(SHORT_WEEK_REGEX)

    if longWeek.match(week_number):
        week_len = len("week")
        longWeek = f"w{week_number[week_len:]}"
        return longWeek
    elif shortWeek.match(week_number):
        return week_number
    else:
        raise DefinitionsException(f"The week number {week_number} is not valid. The week should match {LONG_WEEK_REGEX} or {SHORT_WEEK_REGEX}")

"""
    Returns true if this string represents a week number that can be parsed by
    normalize_week_number
"""
def is_week_number(string):
    string = string.lower()
    longWeek = re.compile(LONG_WEEK_REGEX)
    shortWeek = re.compile(SHORT_WEEK_REGEX)

    return longWeek.match(string) or shortWeek.match(string)

"""
    Parses the date string into a ParsedDefinitionsDate object
"""
def _parse_week_number(week_number: int, week_format):
    pattern = re.compile(FORMAT_REGEX)
    if not pattern.match(week_format):
        raise DefinitionsException(f"Invalid week format provided {week_format}. It should match {FORMAT_REGEX}")

    day = week_format[0:week_format.index("%") - 2]

    time_index = week_format.find("%t")
    hours = 23
    minutes = 59

    if time_index == -1:
        time_index = len(week_format) + 1
    else:
        time = week_format[time_index + 2:]
        time = time.split(":")
        hours = int(time[0])
        minutes = int(time[1])

        if hours < 0 or hours > 23:
            raise DefinitionsException(f"Invalid hour value: {hours} given. Must be in range [0-23]")
        elif minutes < 0 or minutes > 59:
            raise DefinitionsException(f"Invalid minutes value: {minutes} given. Must be in range [0-59]")

    week_format = week_format[week_format.index("%"):time_index - 1]

    if week_format == "%w":
        # just return the week number
        return ParsedDefinitionsDate(day, week_number, hours, minutes)
    else:
        operator = week_format[2:3]
        num = int(week_format[3:])

        if operator == "+":
            return ParsedDefinitionsDate(day, (week_number + num), hours, minutes)
        elif operator == "-":
            if week_number == 1:
                return ParsedDefinitionsDate(day, 1, hours, minutes) # can't go back from week 1
            else:
                week_number = week_number - num
                if week_number < 1:
                    week_number = 1

                return ParsedDefinitionsDate(day, week_number, hours, minutes)

"""
    Retrieve the date represented by the string Day, week_number.
    This date is relative to week 1
"""
def _get_date(week_one, week_number, date: ParsedDefinitionsDate):
    if date is not None:
        date_day = date.day
        date_week = date.week_number
        date_week = date_week - 1 # subtract 1 from the number of weeks to add on to week 1 since week 1 is inclusive

        date_week = _add_weeks(week_one, date_week)
        return _get_date_of_day(date_week, date_day, date.hours, date.minutes)

    return None

"""
    Calculates the 3 dates, returning a tuple start, end, cutoff
    The start_date, end_date and cutoff_date are expected to be already parsed,
    with any %w strings resolved
"""
def _calculate_dates(week_one, week_number, start_date : ParsedDefinitionsDate,
                    end_date: ParsedDefinitionsDate, cutoff_date: ParsedDefinitionsDate):
    if start_date is not None:
        start_date = _get_date(week_one, week_number, start_date)

    if end_date is not None:
        end_date = _get_date(week_one, week_number, end_date)

    if cutoff_date is not None:
        cutoff_date = _get_date(week_one, week_number, cutoff_date)

    return start_date, end_date, cutoff_date

"""
    Returns a tuple of start, end and cut off dates based on the provided week number
    Returns a tuple of (start, end, cutoff)
"""
def calculate_dates(week_number, definitions: dict):
    week_number = normalize_week_number(week_number);
    week_number_val = int(week_number[1:])

    if not 'defWeek01' in definitions:
        return None

    week_one = definitions['defWeek01']

    start_date = None
    if 'defOpenDate' in definitions:
        start_date = definitions['defOpenDate']

    end_date = None
    if 'defDueDate' in definitions:
        end_date = definitions['defDueDate']

    cutoff_date = None
    if 'defCutoffDate' in definitions:
        cutoff_date = definitions['defCutoffDate']

    if start_date is not None:
        start_date = _parse_week_number(week_number_val, start_date)

    if end_date is not None:
        end_date = _parse_week_number(week_number_val, end_date)

    if cutoff_date is not None:
        cutoff_date = _parse_week_number(week_number_val, cutoff_date)

    return _calculate_dates(week_one, week_number_val, start_date, end_date, cutoff_date)

"""
    Validates the provided date format string to ensure that it matches the format
    regex
"""
def validate_date_format(date_format):
    pattern = re.compile(FORMAT_REGEX)
    return pattern.match(date_format)

class DefinitionsException(Exception):
    pass
