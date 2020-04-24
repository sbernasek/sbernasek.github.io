import numpy as np
import pandas as pd
from collections import Counter
from functools import reduce
from operator import add
from modules.utilities import haversine
from modules.utilities import str_to_datetime
from maps.places import PlaceFinder

from pyproj import Geod
from folium import FeatureGroup, Icon, Marker, PolyLine, TileLayer, LayerControl
from folium.features import CustomIcon
from folium.plugins import MarkerCluster, AntPath, HeatMap, HeatMapWithTime


placefinder = PlaceFinder()


class TripSegment:
    
    GPS_INDEX = ['latitude', 'longitude']
    
    def __init__(self, data, owner=None):
        self.data = data
        self.owner = owner
        self._trip_ids = []
        self.connections = []
        self.is_connection = False
        
    def add_connection(self, segment):
        self.connections.append(segment)

    @property
    def legs(self):
        return [self] + self.connections

    @property
    def is_flight(self):
        return False
    
    @property
    def timestamp(self):
        return self.data.index.mean()

    def within(self, *timespans):
        for beginning, end in timespans:
            if type(beginning) == str:
                beginning = str_to_datetime(beginning)
            if type(end) == str:
                end = str_to_datetime(end)
            if self.timestamp < beginning or self.timestamp > end:
                return False
        return True

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
        return list(counts.keys()) + self._trip_ids

    def add_trip_id(self, trip_id):
        if trip_id not in self.trip_ids:
            self._trip_ids.append(trip_id)

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
            return '{:s}, {:s}'.format(location.city, location.state)
        else:
            return '{:s}, {:s}'.format(location.city, location.country)
    
    @property
    def origin_str(self):
        return placefinder(self.origin)

    @property
    def destination_str(self):
        return placefinder(self.destination)
        
    def get_line(self, **kwargs):
        xy = self.data[self.GPS_INDEX].values
        return PolyLine(xy, tooltip=self.caption, **kwargs)
                
    def get_antpath(self, **kwargs):
        xy = self.data[self.GPS_INDEX].values
        return AntPath(xy, tooltip=self.caption, **kwargs)
    
    def get_heatmap(self, radius=7, blur=7, **kwargs):
        
        xy = self.data[self.GPS_INDEX].resample('1H').mean().interpolate()

        heatmap = HeatMap(xy.values,
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

    @property
    def caption(self):
        return 'Flight from {:s} to {:s}'.format(self.origin_str, self.destination_str)

    @property
    def is_flight(self):
        return True

    @staticmethod
    def interpolate_great_circle(start, stop, N=30):
        geoid = Geod(ellps="WGS84")
        middle = geoid.npts(*start[::-1], *stop[::-1], N)
        pts = [tuple(start)] + [pt[::-1] for pt in middle] + [tuple(stop)]
        return np.array(pts)
        
    def get_line(self, N=25, **kwargs):
        xy = self.data[self.GPS_INDEX].values    
        route = self.interpolate_great_circle(xy[0], xy[-1])
        return PolyLine(route, tooltip=self.caption, **kwargs)


class TrainSegment(TripSegment):
    @property
    def caption(self):
        return 'Train from {:s} to {:s}'.format(self.origin_str, self.destination_str)

class DriveSegment(TripSegment):

    @property
    def caption(self):
        return 'Roadtrip from {:s} --> {:s}'.format(self.origin_str, self.destination_str)

    @property
    def trip_ids(self):
        counts = Counter(reduce(add, self.data.trip_id.values))
        return [k for k,v in counts.items() if v > 3]

    def get_antpath(self, 
                    freq=None,
                    min_velocity=1, 
                    min_distance=10, **kwargs):

        PINGS = self.data

        if min_velocity is not None:
            faster = PINGS.window_velocity > min_velocity
            PINGS = PINGS[faster]

        if min_distance is not None:    
            further = PINGS.window_max_distance > min_distance
            PINGS = PINGS[further]

        PINGS = PINGS[self.GPS_INDEX]

        if freq is not None:
            PINGS = PINGS.resample(freq).mean().interpolate()


        xy = PINGS.values.tolist()        
        ballistic = [xy[0]]
        for pt in xy:
            distance = haversine(ballistic[-1], pt)    
            if distance >= 5:
                ballistic.append(pt)
        ballistic.append(xy[-1])

        return AntPath(ballistic, tooltip=self.caption, **kwargs)











# from sklearn.cluster import MeanShift

# # cluster photos
# photos = posts[~posts.latitude.isna()]
# photos.loc[:, 'gallery'] = None
# for idx, album in photos.groupby('album'):
#     model = MeanShift(bandwidth=1.).fit(album[Pings.GPS_INDEX].values)
#     gallery_base = '-'.join([x.lower() for x in idx.split()])
#     labels = [gallery_base+'{:d}'.format(_id) for _id in model.labels_]
#     photos.loc[album.index, 'gallery'] = labels

