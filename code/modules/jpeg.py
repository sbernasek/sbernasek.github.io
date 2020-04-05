from PIL import Image, ExifTags


class GPS:
    
    def __init__(self, info):
        self.info = info
        
    @staticmethod
    def from_exif(exif):        
        info = {}
        if 'GPSInfo' in exif:
            for key in exif['GPSInfo'].keys():
                info[ExifTags.GPSTAGS[key]] = exif['GPSInfo'][key]
        return GPS(info)

    @property
    def coordinates(self):
        coords = {}
        for key in ['Latitude', 'Longitude']:
            if 'GPS'+key in self.info and 'GPS'+key+'Ref' in self.info:
                e = self.info['GPS'+key]
                ref = self.info['GPS'+key+'Ref']
                coords[key] = ( str(e[0][0]/e[0][1]) + '°' +
                              str(e[1][0]/e[1][1]) + '′' +
                              str(e[2][0]/e[2][1]) + '″ ' +
                              ref )

        if 'Latitude' in coords and 'Longitude' in coords:
            return [coords['Latitude'], coords['Longitude']]
        else:
            return [None, None]

    @property
    def decimal_coordinates(self):
        coords = {}
        for key in ['Latitude', 'Longitude']:
            if 'GPS'+key in self.info and 'GPS'+key+'Ref' in self.info:
                e = self.info['GPS'+key]
                ref = self.info['GPS'+key+'Ref']
                coords[key] = ( e[0][0]/e[0][1] +
                              e[1][0]/e[1][1] / 60 +
                              e[2][0]/e[2][1] / 3600
                            ) * (-1 if ref in ['S','W'] else 1)

        if 'Latitude' in coords and 'Longitude' in coords:
            return [coords['Latitude'], coords['Longitude']]
        else:
            return [None, None]


class JPEG_Metadata:
    
    def __init__(self, path):
        self.path = path
        im = Image.open(path)
        self.exif = self.extract_exif(im)
    
    def to_record(self):
        return {
            'path': self.path,
            'filename': self.filename,
            'time_shot': self.time_shot,
            'time_rendered': self.time_rendered,
            'gps': self.gps.decimal_coordinates,
            'model': self.model}

    @property
    def filename(self):
        return self.path.rsplit('/', maxsplit=1)[-1]
    
    @property
    def time_shot(self):
        return self.exif['DateTimeOriginal']

    @property
    def time_rendered(self):
        return self.exif['DateTime']
   
    @property
    def gps(self):
        return GPS.from_exif(self.exif)
    
    @property
    def model(self):
        return self.exif['Model']
    
    @staticmethod
    def extract_exif(im):
        return {ExifTags.TAGS[k]: v for k,v in im._exif.items() if k in ExifTags.TAGS}
        
        
