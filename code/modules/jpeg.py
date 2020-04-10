from exif import Image as ExifImage
from iptcinfo3 import IPTCInfo

import logging
iptcinfo_logger = logging.getLogger('iptcinfo')
iptcinfo_logger.setLevel(logging.ERROR)

from modules.utilities import str_to_datetime, localize_datetime, gps_to_decimal


class JPEG_Metadata:
    
    def __init__(self, path):
        self.path = path
        self.exif = self.extract_exif(path)
        self.iptc = IPTCInfo(path)

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
    def time_shot_local(self):
        return self.exif.datetime_original

    @property
    def time_shot_pst(self):

        keywords = [str(x, 'utf-8') for x in self.iptc['keywords']]
        for tz in ['pst', 'mst', 'gmt', 'cet', None]:
            if tz in keywords:
                break
        if tz is None:
            print(self.path)
            print(self.iptc['keywords'])
            raise ValueError('Timezone not found in file IPTC info.')

        return localize_datetime(self.time_shot_local, tz)

    @property
    def timestamp(self):
        return str_to_datetime(self.time_shot_pst)

    @property
    def time_rendered(self):
        return self.exif.datetime

    @property
    def geotagged(self):
        if self.latitude is not None:
            return True
        else:
            return False

    @property
    def latitude(self):
        try:
            return gps_to_decimal(*self.exif.gps_latitude)
        except:
            return None

    @property
    def longitude(self):
        try:
            return -gps_to_decimal(*self.exif.gps_longitude)
        except:
            return None

    def to_record(self):
        return {
            'source': self.source,
            'filename': self.filename,
            'path': self.path,
            'timestamp': self.timestamp,
            'time_shot_pst': self.time_shot_pst,
            'time_shot_local': self.time_shot_local,
            'time_rendered': self.time_rendered,
            'geotagged': self.geotagged,
            'latitude': self.latitude,
            'longitude': self.longitude
        }
