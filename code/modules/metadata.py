from os.path import join, exists
from glob import glob
import pandas as pd

from modules.utilities import str_to_datetime
from modules.jpeg import JPEG_Metadata


class PhotoMetadata:
    
    INDEX = ['album', 'filename', 'source']
    
    def __init__(self, path=None):
        self.path = path
        
        if path is not None and exists(path):
            self.load()
        else:
            self.initialize()
                
    def load(self):
        self.data = self._load(self.path)
        
    def initialize(self):
        columns = [
            'source',
            'filename',
            'album',
            'path',
            'timestamp',
            'time_shot_pst',
            'time_shot_local',
            'time_rendered',
            'geotagged',
            'latitude',
            'longitude'
            ]

        self.data = pd.DataFrame(columns=columns)
        self.data = self.data.set_index(self.INDEX)
    
    @staticmethod
    def _load(path):
        return pd.read_hdf(path, 'data')
    
    def save(self, path=None):
        if path is None:
            if self.path is None:
                raise ValueError('No path specified.')
            path = self.path
            
        self.data.to_hdf(path, 'data')
    
    def add_image(self, img_path, album):
        
        # build image metadata record
        img_record = JPEG_Metadata(img_path).to_record()
        
        # build index
        filename = img_record.pop('filename')
        source = img_record.pop('source')
        
        # compile series
        record = pd.Series(img_record)
        record.name = (album, filename, source)
        
        # save record
        self.data = self.data.append(record, ignore_index=False)
        
    def add_album(self, dirpath, name):
        img_paths = glob(join(dirpath, '*.j*'))
        for i, img_path in enumerate(img_paths):
            self.add_image(img_path, album=name)
            
    @staticmethod
    def _time_rendered(img_path):
        return JPEG_Metadata(img_path).time_rendered
    
    def update_render_times(self):
        self.data.time_rendered = self.data.path.apply(self._time_rendered)
    
    @property
    def render_times(self):
        return self.data.time_rendered.apply(str_to_datetime)
    
