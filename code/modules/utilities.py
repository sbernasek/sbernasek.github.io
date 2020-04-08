import json
from datetime import datetime
import math
import numpy as np
from postal.parser import parse_address


def read_json(filepath):
    with open(filepath, 'r') as file:
        content = json.load(file)
    return content


def posix_to_ts(t_posix):
    return datetime.fromtimestamp(int(t_posix)/1000)


def str_to_datetime(time_str, fmt='%Y:%m:%d %H:%M:%S'):
    return datetime.strptime(time_str, fmt)


def datetime_to_str(ts, fmt='%Y:%m:%d %H:%M:%S'):
    return ts.strftime(fmt)


def localize_datetime(time_str, tz, fmt='%Y:%m:%d %H:%M:%S'):
    shifts = {'pst': 0, 'mst': 1, 'gmt': 8, 'cet': 9}
    ts = str_to_datetime(time_str, fmt)
    dt = timedelta(hours=shifts[tz])
    ts_localized = ts - dt
    return datetime_to_str(ts_localized, fmt)


def gps_to_decimal(d, m, s):
    return d + (m/60) + (s/3600)


def fmt_address(address):
    if address is None:
        return {}
    else:
        return dict([(v,k) for k,v in parse_address(address)])


def isblank(x):
    if x is None or x == '':
        return True
    elif type(x) == float:
        return np.isnan(x)
    else:
        return False


def haversine(coord1, coord2):
    R = 6372.8 / 1.6  # Earth radius in mi
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    
    phi1, phi2 = math.radians(lat1), math.radians(lat2) 
    dphi       = math.radians(lat2 - lat1)
    dlambda    = math.radians(lon2 - lon1)
    
    a = math.sin(dphi/2)**2 + \
        math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    
    return 2*R*math.atan2(math.sqrt(a), math.sqrt(1 - a))
