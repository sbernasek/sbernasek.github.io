from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS


class GPS:
    
    SIGNS = dict(N=1, S=-1, E=1, W=-1)
    
    def __init__(self, filepath):
        self.exif = self.get_exif(filepath)
        
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
    def decimal_coordinates(self):
        for key in ['Latitude', 'Longitude']:
            if 'GPS'+key in self.exif and 'GPS'+key+'Ref' in self.exif:
                e = self.exif['GPS'+key]
                ref = self.exif['GPS'+key+'Ref']
                self.exif[key] = ( e[0][0]/e[0][1] +
                              e[1][0]/e[1][1] / 60 +
                              e[2][0]/e[2][1] / 3600
                            ) * (-1 if ref in ['S','W'] else 1)

        if 'Latitude' in self.exif and 'Longitude' in self.exif:
            return (self.exif['Latitude'], self.exif['Longitude'])
        else:
            return (None, None)

    @property
    def longitude_ref(self):
        return self.exif['GPSInfo']['GPSLongitudeRef']
    
    @property
    def latitude_ref(self):
        return self.exif['GPSInfo']['GPSLatitudeRef']
