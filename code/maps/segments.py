import numpy as np
import pandas as pd
from collections import Counter
from functools import reduce
from operator import add
from modules.utilities import haversine
from folium import FeatureGroup, Icon, Marker, PolyLine, TileLayer, LayerControl
from folium.features import CustomIcon
from folium.plugins import MarkerCluster, AntPath, HeatMap, HeatMapWithTime


class TripSegment:
    
    GPS_INDEX = ['latitude', 'longitude']
    
    def __init__(self, data, owner=None):
        self.data = data
        self.owner = owner
        
    @property
    def start(self):
        return self.data.index.values[0]
    
    @property
    def stop(self):
        return self.data.index.values[-1]
    
    @property
    def start_ts(self):
        return pd.Timestamp(self.start).strftime('%Y-%m-%d %T')

    @property
    def stop_ts(self):
        return pd.Timestamp(self.stop).strftime('%Y-%m-%d %T')

    @property
    def dt(self):
        return self.stop-self.start
    
    @property
    def trip_id(self):
        counts = Counter(reduce(add, self.data.trip_id.values))
        return counts.most_common(n=1)[0][0]

    @property
    def trip_ids(self):
        counts = Counter(reduce(add, self.data.trip_id.values))
        return list(counts.keys())

    @property
    def time_period(self):
        counts = Counter(reduce(add, self.data.time_period.values))
        return counts.most_common(n=1)[0][0]
    
    @property
    def origin(self):
        return self.data.iloc[0]
        
    @property
    def destination(self):
        return self.data.iloc[-1]
    
    @property
    def international(self):
        return self.origin.country != self.destination.country
    
    @property
    def countries(self):
        return self.data.country.unique().tolist()

    @property
    def states(self):
        return self.data.state.unique().tolist()

    @property
    def cities(self):
        return self.data.city.unique().tolist()
    
    @staticmethod
    def fmt_location(location):
        
        if location.country == 'US':
            return '{:s}, {:s}'.format(location.state, location.country)
        else:
            return '{:s}'.format(location.country)
    
    @property
    def caption(self):
        origin_str = self.fmt_location(self.origin)
        destination_str = self.fmt_location(self.destination)
        caption = '{:s} --> {:s}'.format(origin_str, destination_str)
        return caption
        
    def get_line(self, **kwargs):
        xy = self.data[self.GPS_INDEX].values
        return PolyLine(xy, tooltip=self.caption, **kwargs)
                
    def get_antpath(self, **kwargs):
        xy = self.data[self.GPS_INDEX].values
        return AntPath(xy, tooltip=self.caption, **kwargs)
    
    def get_heatmap(self, radius=7, blur=7, **kwargs):
        xy = self.data[self.GPS_INDEX].values
        heatmap = HeatMap(xy,
                          radius=radius,
                          blur=blur,
                          **kwargs)
        
        return heatmap

    @staticmethod
    def rolling_window(a, window):
        shape = a.shape[:-1] + (a.shape[-1] - window + 1, window)
        strides = a.strides + (a.strides[-1],)
        return np.lib.stride_tricks.as_strided(a, shape=shape, strides=strides)

    def get_heatmap_video(self, 
                            radius=10, 
                            auto_play=True,
                            resolution='h', 
                            window_size=1):

        # resample
        xy = self.data[self.GPS_INDEX]
        xy = xy.resample(resolution).mean().interpolate(limit_direction='both').values

        windows = self.rolling_window(np.arange(len(xy)), window_size)
        xy = xy[windows].tolist()

        # build heatmap
        heatmap = HeatMapWithTime(xy, 
            auto_play=auto_play, 
            display_index=False, 
            radius=radius, 
            index_steps=1,
            min_speed=1, 
            max_speed=24, 
            speed_step=1)

        return heatmap


class FlightSegment(TripSegment):
    pass

class TrainSegment(TripSegment):
    pass

class DriveSegment(TripSegment):

    @property
    def trip_ids(self):
        counts = Counter(reduce(add, self.data.trip_id.values))
        return [k for k,v in counts.items() if v > 3]





# from sklearn.cluster import MeanShift

# # cluster photos
# photos = posts[~posts.latitude.isna()]
# photos.loc[:, 'gallery'] = None
# for idx, album in photos.groupby('album'):
#     model = MeanShift(bandwidth=1.).fit(album[Pings.GPS_INDEX].values)
#     gallery_base = '-'.join([x.lower() for x in idx.split()])
#     labels = [gallery_base+'{:d}'.format(_id) for _id in model.labels_]
#     photos.loc[album.index, 'gallery'] = labels

