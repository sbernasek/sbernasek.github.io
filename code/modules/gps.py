from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS


class GPS:
    
    SIGNS = dict(N=1, S=-1, E=1, W=-1)
    
    def __init__(self, filepath):
        self.exif = self.get_exif(filepath)

    @property
    def exif_gps(self):
        return self.exif['GPSInfo']
    
    @staticmethod
    def get_exif(filepath):
        exif = Image.open(filepath)._getexif()

        if exif is not None:
            for key, value in exif.items():
                name = TAGS.get(key, key)
                exif[name] = exif.pop(key)

            if 'GPSInfo' in exif:
                for key in exif['GPSInfo'].keys():
                    name = GPSTAGS.get(key,key)
                    exif['GPSInfo'][name] = exif['GPSInfo'].pop(key)

        return exif
    
    @property
    def latitude(self):

        if 'GPSInfo' not in self.exif:
            return None

        elif 'GPSLatitude' not in self.exif_gps or 'GPSLatitudeRef' not in self.exif_gps:
            return None

        else:
            e = self.exif_gps['GPSLatitude']
            ref = self.exif_gps['GPSLatitudeRef']
            return ( e[0][0]/e[0][1] +
                      e[1][0]/e[1][1] / 60 +
                      e[2][0]/e[2][1] / 3600
                    ) * (-1 if ref in ['S','W'] else 1)

    @property
    def longitude(self):

        if 'GPSInfo' not in self.exif:
            return None

        elif 'GPSLongitude' not in self.exif_gps or 'GPSLongitudeRef' not in self.exif_gps:
            return None

        else:
            e = self.exif_gps['GPSLongitude']
            ref = self.exif_gps['GPSLongitudeRef']
            return ( e[0][0]/e[0][1] +
                      e[1][0]/e[1][1] / 60 +
                      e[2][0]/e[2][1] / 3600
                    ) * (-1 if ref in ['S','W'] else 1)

    @property
    def decimal_coordinates(self):
        return (self.latitude, self.longitude)
        
    @property
    def longitude_ref(self):
        return self.exif_gps['GPSLongitudeRef']
    
    @property
    def latitude_ref(self):
        return self.exif_gps['GPSLatitudeRef']
