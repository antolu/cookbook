from datetime import timedelta, date, datetime
from string import Template

import re

from .utilities import DotDict


def parse_type(item: str):
    """
    Attempts to parse the item into a python representation, eg. 2 hours to a timedelta object

    Parameters
    ----------
    item : str
        The item to convert to python

    Returns
    -------
    item : timedelta or int or str
        Returns the converted object, or if no conversion has been executed; the original string.

    """
    for r in _regex.keys():
        if r.match(item) is not None:
            return _regex[r].function(item)

    return item  # No matches


def to_string(item):
    """
    Attempts to convert an item to a human readable string representation, eg. 2:00:00 (timedelta object) to '2 hours'.

    Currently parses timedelta, datetime, and boolean objects.

    Parameters
    ----------
    item : any
        Any object that will be converted to string form.

    Returns
    -------
    item: str
        Returns the converted object, or if no conversion has been executed; the original object.

    """
    if isinstance(item, timedelta):
        return duration_str(item)
    elif isinstance(item, date):
        return item.strftime('%Y-%m-%d')
    elif isinstance(item, bool):
        return 'yes' if item else 'no'
    return item  # no match


def strfdelta(tdelta: timedelta, fmt: str) -> str:
    """
    Intended to be analogous to datetimes strftime, this formats a timedelta object to an arbitrary output string.
    Currently does not support time formats larger than hours, or shorter than seconds, however this is easily added if
    necessary.

    Parameters
    ----------
    tdelta : timedelta
        The timedelta object to strip time data from.
    fmt : str
        A python format on how to strip the timedelta information


    Returns
    -------
    t : str
        A string representation of a timedelta object based on the format

    See Also
    --------
    Check out https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior for information about the
    intended behaviour.

    """
    d = dict()
    hours, remainder = divmod(tdelta.seconds, 3600)
    d['H'] = hours
    d['M'], d['S'] = divmod(remainder, 60)
    t = _DeltaTemplate(fmt)
    return t.substitute(**d)


def duration_str(tdelta: timedelta) -> str:
    """
    Formats a timedelta object from for example 2:00:00 object to '2 hours', and 2:30:00 to '2 hours 30 minutes.

    Parameters
    ----------
    tdelta : timedelta
        The timedelta object to read time information from.

    Returns
    -------
    output: str
        The string representation of the timedelta object (x hours y minutes).

    """
    hours, remainder = divmod(tdelta.seconds, 3600)
    minutes, _ = divmod(remainder, 60)

    output = ''
    if hours > 0:
        output += '{} hour{}'.format(hours, '' if hours == 1 else 's')
    if minutes > 0:
        output += '{} minute{}'.format(minutes, '' if minutes == 1 else 's')

    return output


def _handle_duration(data: str) -> timedelta:
    """
    Internal method. Attempts to parse a string into a timedelta object based on the format
    'X hour(s) Y minute(s)' using regular expressions.

    Parameters
    ----------
    data : str
        The string to parse information from.

    Returns
    -------
    t: timedelta
        A timedelta object based on the input string

    Raises
    ------
    ValueError:
        If the input data is does not conform to the coded format.

    """
    regex = re.compile(r'^((?P<hours>\d+)\s?(hour(s)?|h))?\s?((?P<minutes>\d+)\s?(minute(s)?|m))?$', re.IGNORECASE)

    parts = regex.match(data)

    if parts is None:
        raise ValueError(f'Could not parse data {data} as a timedelta')

    parts = parts.groupdict()
    time_params = dict()
    for (name, param) in parts.items():
        try:
            if param:
                time_params[name] = int(param)
        except ValueError:
            pass

    return timedelta(**time_params)


def _handle_temperature(data: str) -> int:
    """
    Internal method. Attempts to parse a string into an int from the format 'X degrees' / 'X C'.

    Parameters
    ----------
    data : str
        The string to parse information from.

    Returns
    -------

    Raises
    ------
    ValueError:
        If the input data does not conform to the regex format (no data to strip could be found).

    """
    regex = re.compile(r'^(?P<temperature>\d+)\s?(degrees|C)$', re.IGNORECASE)

    m = regex.match(data)
    if not m:
        raise ValueError(f'Could not parse data {data} as temperature')

    m = m.groupdict()
    if m['temperature']:
        return int(m['temperature'])
    else:
        raise ValueError(f'Could not find temperature from string {data}')


def _handle_bool(data: str) -> bool:
    """
    Internal method. Attempts to parse a human readable string as a boolean.

    Parameters
    ----------
    data : str
        The string to parse information from.

    Returns
    -------
    bool:
        True if the string can be interpreted as 'yes', or False if the string can be interpreted as 'no'.

    Raises
    ------
    ValueError:
        If the parsed data cannot be parsed as a boolean.
    """
    data = data.lower()

    if data == 'no' or data == 'false':
        return False
    elif data == 'yes' or data == 'true':
        return True
    else:
        raise ValueError('Passed value [{data}] is not a valid boolean.')


def _handle_date(data: str) -> date:
    """
    Internal method. Attempts to parse a sting as a date.

    Parameters
    ----------
    data : str
        The string to parse information from.

    Returns
    -------
    datetime
        A datetime object with information stripped from the data.

    """
    # TODO: handle more dae formats
    return datetime.strptime(data, '%Y-%m-%d').date()


class _DeltaTemplate(Template):
    """
    Helper class, to help convert timedelta objects into strings using the strftime method.
    """
    delimiter = '%'


"""
A mapping from regex match to a function to handle the regex match.
"""
_regex = DotDict({
    re.compile(r'^(\d+)\s?(degrees|C)$', re.IGNORECASE): {  # temperature
        'function': _handle_temperature,
    },
    re.compile(r'^(\d+\s?(hours|h))?\s?(\d+\s?(minutes|m))?$', re.IGNORECASE): {  # duration
        'function': _handle_duration,
    },
    re.compile(r'^\d{4}-?\d{1,2}-?\d{1,2}$', re.IGNORECASE): {
        'function': _handle_date,
    },
    re.compile(r'^(no|yes|true|false)$', re.IGNORECASE): {
        'function': _handle_bool,
    }

})
