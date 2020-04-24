from datetime import datetime, timedelta, time
import pytz

from exif import Image as ExifImage
from iptcinfo3 import IPTCInfo

import logging
iptcinfo_logger = logging.getLogger('iptcinfo')
iptcinfo_logger.setLevel(logging.ERROR)

from modules.gps import GPS
from modules.utilities import datetime_to_str, str_to_datetime, localize_datetime, gps_to_decimal

import googlemaps
with open('../../data/keys.txt', 'r') as file:
    api_key = file.read().strip()


GOOGLE_API = googlemaps.Client(key=api_key)
NUM_API_CALLS = 0


def query_utc(naive_dt, tz, location=None):

    global GOOGLE_API
    global NUM_API_CALLS
    
    local = pytz.timezone(tz)
    utc_dt_est = local.localize(naive_dt, is_dst=None).astimezone(pytz.utc)

    if location is None:
        TIMEZONE_LOCATIONS = {
            'America/Los_Angeles': (34.0207305, -118.6919147),
            'MST': (40.7767168,-111.9905247),
            'EST': (40.6976637,-74.1197638),
            'CET': (41.9102415,12.3959152),
            'GMT': (51.5287718,-0.2416803)}
        location = TIMEZONE_LOCATIONS[tz]

    # query API
    NUM_API_CALLS += 1
    RESPONSE = GOOGLE_API.timezone(location, utc_dt_est.timestamp())
    tz_dst_offset = RESPONSE['dstOffset']
    tz_raw_offset = RESPONSE['rawOffset']
    tz_utc_offset = tz_raw_offset + tz_dst_offset
    #tz_id = RESPONSE['timeZoneId']
    #tz_name = RESPONSE['timeZoneName']
    #tz_is_dst = tz_dst_offset != 0    

    utc_time = naive_dt - timedelta(seconds=tz_utc_offset)

    return datetime_to_str(utc_time)



class JPEG_Metadata:
    
    def __init__(self, path):
        self.path = path
        self.exif = self.extract_exif(path)
        self.iptc = IPTCInfo(path)
        latitude, longitude = GPS(path).decimal_coordinates
        self.latitude = latitude
        self.longitude = longitude

    @staticmethod
    def extract_exif(filepath):
        with open(filepath, 'rb') as file:
            exif = ExifImage(file)
        return exif

    @property
    def filename(self):
        return self.path.rsplit('/', maxsplit=1)[-1]

    @property
    def source(self):
        try:
            return self.exif.model
        except:
            return 'Other'

    @property
    def tz_keyword(self):
        keywords = [str(x, 'utf-8') for x in self.iptc['keywords']]
        for tz in ['pst', 'mst', 'est', 'gmt', 'cet', None]:
            if tz in keywords:
                break
        if tz is None:
            raise ValueError('Timezone not found in file IPTC info.')
        
        tz_names = dict(pst='America/Los_Angeles', 
                        mst='MST', est='EST', cet='CET', gmt='GMT')

        return tz_names[tz]

    @property
    def time_shot_local(self):
        return self.exif.datetime_original

    @property
    def time_shot_utc(self):
        """
        Four cases:
        
        1. GPS time included --> in UTC already
        2. GPS included, no GPS time --> TimeZones API to get UTC
        3. No GPS, but local time --> TimeZones API to get UTC, using KW for location
        4. No GPS, non-local (camera) --> constant offset to UTC
        
        """
        
        # Case 1
        if self.geotagged:
            
            try:

                UTC_DATE = self.exif.gps_datestamp
                UTC_TIME = self.exif.gps_timestamp
                UTC_TIMESTAMP = UTC_DATE + ' ' + '{:02d}:{:02d}:{:02d}'.format(*[int(t) for t in UTC_TIME])

                # make sure GPS time matches local time (rare, but happens)
                to_time = lambda x: time(int(x[0]), int(x[1]), int(x[2]//1))
                LOCAL_TIME = str_to_datetime(self.exif.datetime_original)
                delta = lambda x,y: abs((x.minute-y.minute)*60 + (x.second-y.second))
                if delta(to_time(UTC_TIME), LOCAL_TIME.time()) > 60:
                    raise ValueError('GPS Timestamp is off.')

            except:
                location = (self.latitude, self.longitude)
                naive_dt = str_to_datetime(self.time_shot_local)                
                UTC_TIMESTAMP = query_utc(naive_dt, self.tz_keyword, location=location)
        
        else:
            
            # CASE 3
            if 'iPhone' in self.source:
                naive_dt = str_to_datetime(self.time_shot_local)                
                UTC_TIMESTAMP = query_utc(naive_dt, self.tz_keyword, location=None)
            
            # CASE 4: 
            # Initially, camera was in EST, 5h behind UTC
            # As of 2019-10-09 camera was in PST, 8h behind UTC 
            else:

                camera_dt = str_to_datetime(self.time_shot_local)

                if camera_dt <= str_to_datetime('2019:10:09 00:00:00'):
                    UTC_OFFSET = timedelta(hours=5)
                else:
                    UTC_OFFSET = timedelta(hours=8)

                utc_dt = camera_dt + UTC_OFFSET
                UTC_TIMESTAMP = datetime_to_str(utc_dt)
        
        return UTC_TIMESTAMP
        
    @property
    def timestamp(self):
        return str_to_datetime(self.time_shot_utc)

    @property
    def time_rendered(self):
        return self.exif.datetime

    @property
    def geotagged(self):
        if self.latitude is not None:
            return True
        else:
            return False

    def to_record(self):

        # limit API calls
        time_shot_utc = self.time_shot_utc
        timestamp = str_to_datetime(time_shot_utc)

        return {
            'source': self.source,
            'filename': self.filename,
            'path': self.path,
            'timestamp': timestamp,
            'time_shot_utc': time_shot_utc,
            'time_shot_local': self.time_shot_local,
            'time_rendered': self.time_rendered,
            'geotagged': self.geotagged,
            'latitude': self.latitude,
            'longitude': self.longitude
        }
