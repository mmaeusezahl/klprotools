import struct
import datetime

# This fixpoint was extracted by reverse engineering
_fixed_point_datetime = datetime.datetime(2019, 9 ,13, 14, 0, 0)
_fixed_point_julian_seconds = 212435186400

def julian_seconds_to_datetime(julian_seconds):
    """This function converts seconds according to the 
    `Julian Day <https://en.wikipedia.org/wiki/Julian_day>`_ to the internal
    datetime representation. It is only accurate to seconds (milliseconds are
    not supported).

    :param julian_seconds: seconds since 12:00:00, January 1, 4713 BC
    :type julian_seconds: int
    :return: datetime object
    :rtype: datetime.datetime
    """
    return _fixed_point_datetime + datetime.timedelta(
                           seconds=julian_seconds - _fixed_point_julian_seconds)

def datetime_to_julian_seconds(date):
    """This function converts datetime objects to seconds according to the 
    `Julian Day <https://en.wikipedia.org/wiki/Julian_day>`_. It is only 
    accurate to seconds (milliseconds are not supported).

    :param date: datetime object
    :type date: datetime.datetime
    :return: seconds since 12:00:00, January 1, 4713 BC
    :rtype: int
    """
    return int(_fixed_point_julian_seconds + 
                                 (date - _fixed_point_datetime).total_seconds())


def print_hex(b):
    for a in b:
        print(a.hex())

def read_file(path, yield_illegal_dates = False):
    """Reads a history file which was created by the 'KlimaLogg Pro' software.
    This function can recognize simple errors which might occur if the battery
    of the 'KlimaLogg Pro' device runs low and silently skip them.

    If the parameter `yield_illegal_dates` is True, it will instead return the
    date None for the respective entries.

    :param path: path to the history file
    :type path: str
    :param yield_illegal_dates: If this parameter is True, the function will
        return None as date for otherwise illegal entries, defaults to False.
    :type yield_illegal_dates: bool, optional
    :yield: Tuples (date, data) where date is a datetime and data is a list of 
        9 tuples which are each composed of two floats. These tuples (temp, 
        hum) correspond to the temperature (temp in °C) and humidity (in %)
        of each of the 9 channels in the order internal, ch. 1, ch. 2, ...
        Temperature and humidity might be None if the respective sensor was not
        connected.
    :rtype: (datetime, [(float, float), ...])
    """
    # the data comes in chunks of 84 bytes
    chunk_size = 84

    with open(path, "rb") as f:
        # read the next chunk from the file
        byte = f.read(chunk_size)

        # this loops over all chunks (entries) in the file
        while byte:
            # first try to read and interpret the time (stored as an unsigned 
            # long)
            try:
                val, = struct.unpack_from("<q", byte, 0)
                date = julian_seconds_to_datetime(val/1000000)
            except OverflowError:
                # this typically means that there was some illegal data in the
                # file e.g. the date with the internal representation 0
                if yield_illegal_dates:
                    date = None
                else:
                    # Read the next chunk of data and continue
                    byte = f.read(chunk_size)
                    continue
            
            # The next step is to extract the temperatures and humidities for 
            # all channels. Note that channel '0' is the internal sensor
            data = []
            for ch_id in range(9):
                temp, hum = struct.unpack_from("<ff", byte, 8 + ch_id * 8)

                # It is not secure that these criteria are correct, but it seems
                # to be the case. A temperature above 80°C is well above the
                # specs anyway and a humidity beyond 100% is invalid.
                if temp > 80: temp = None
                if hum > 101: hum  = None

                data.append((temp, hum))

            # Finally yield the data
            yield date, data

            # Read the next chunk of data
            byte = f.read(chunk_size)

_NONE_TEMP = 0x3333a242 # ~ 81.1°C
_NONE_HUM  = 0x0000dc42 # ~110.0%
_NONE_DATE = 0x0000000000000000

def write_file(path, all_entries):
    with open(path, "wb") as f:
        for date, data in all_entries:
            if date is None:
                f.write(struct.pack('<q', _NONE_DATE))
            else:
                julian_seconds = datetime_to_julian_seconds(date)
                f.write(struct.pack('<q', julian_seconds * 1000000))
            
            if len(data) != 9:
                raise ValueError('Incorrect number of channels. Expected 9 ' +
                    'but got {} for date {}!'.format(len(data), date))

            for temp, hum in data:
                f.write(struct.pack('<f', _NONE_TEMP if temp is None else temp))
                f.write(struct.pack('<f', _NONE_HUM  if hum  is None else hum ))

            # there are empty/unused four bytes at the end
            # they seem to be zero all the time
            f.write(struct.pack('<I',0))