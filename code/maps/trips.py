import numpy as np
import pandas as pd
from sklearn.cluster import MeanShift
from folium import Map, TileLayer, Icon
from folium import FeatureGroup, LayerControl, Marker
from folium.plugins import MarkerCluster, BeautifyIcon

from modules.utilities import haversine
from maps.popup import ImagePopup
from maps.maps import FoliumMap
from maps.segments import TripSegment
from maps.segments import TrainSegment, FlightSegment, DriveSegment


class Trip:

    GPS_INDEX = ['latitude', 'longitude']

    def __init__(self, segments, pings, photos):
        self.segments = segments
        self.pings = pings
        self.photos = photos

    @property
    def air(self):
        return self.segments['air']

    @property
    def rail(self):
        return self.segments['rail']

    @property
    def land(self):
        return self.segments['land']
    
    @property
    def bounds(self):
        df = pd.concat([x.data for x in self.segments['land']])[self.GPS_INDEX].sort_index()
        start, finish = df.iloc[0], df.iloc[-1]
        return start.values, finish.values

    @property
    def centroid(self):
        land = pd.concat([x.data for x in self.segments['land']]).sort_index()
        xy = land[self.GPS_INDEX]
        xy = xy.resample('h').mean().interpolate(limit_direction='both').values
        return xy.mean(axis=0)

    def cluster_photos(self):
        self.photos.loc[:, 'gallery'] = None
        for idx, album in self.photos.groupby('album'):
            model = MeanShift(bandwidth=1.).fit(album[self.GPS_INDEX].values)
            gallery_base = '-'.join([x.lower() for x in idx.split()])
            labels = [gallery_base+'{:d}'.format(_id) for _id in model.labels_]
            self.photos.loc[album.index, 'gallery'] = labels

    def build_map(self, 
                  zoom_start=5,
                  max_zoom=15,
                  **kwargs):

        # create map
        m = Map(width='100%', height='100%',
                tiles='cartodbpositron',
                location=self.centroid, 
                zoom_start=zoom_start,
                max_zoom=max_zoom, **kwargs)

        # add tiles
        TileLayer('openstreetmap', show=False, overlay=True).add_to(m)
        
        # add feature group
        self.fgs = {}
        self.map = m

    def add_layer_control(self, **kwargs):
        LayerControl(**kwargs).add_to(self.map)

    def add_travel_to_map(self, 
        flight_color='black',
        train_color='blue',
        drive_color='red',
        weight=3):

        # add feature group
        self.fgs['air'] = FeatureGroup('Flights', show=False).add_to(self.map)
        self.fgs['land'] = FeatureGroup('Road & Rail', show=True).add_to(self.map)

        # add start/finish
        icon_kw = dict(icon_shape='marker',
                        border_width=2,
                        text_color='black', 
                        border_color='black', 
                        background_color='white', 
                        inner_icon_style='font-size:14px; padding-top:-1px;')
        start, finish = self.bounds
        start_icon = BeautifyIcon('arrow-down', **icon_kw)
        finish_icon = BeautifyIcon('plane', **icon_kw)
        _ = Marker(start, icon=start_icon).add_to(self.fgs['land'])
        _ = Marker(finish, icon=finish_icon).add_to(self.fgs['land'])


        # add segments
        for flight in self.air:
            obj = flight.get_line(color=flight_color, weight=weight, opacity=0.2)
            obj.add_to(self.fgs['air'])
            
        for train in self.rail:
            obj = train.get_line(color=train_color, weight=weight, opacity=0.2)
            obj.add_to(self.fgs['land'])
            
        for drive in self.land:
            options = {'smoothFactor': 10}
            obj = drive.get_antpath(color=drive_color, weight=weight, options=options)
            obj.add_to(self.fgs['land'])

    def add_photos_to_map(self, 
                          clustered=True,
                          maxClusterRadius=20,
                          disableClusteringAtZoom=15,
                          zoomToBoundsOnClick=False,
                          spiderfyOnMaxZoom=True,
                          icon_color='#b3334f',
                          groupby=None,
                          **kwargs):

        # add feature group
        self.fgs['photos'] = FeatureGroup('Photos', show=True).add_to(self.map)

        # create photo cluster object
        if clustered:
            dst = MarkerCluster(
                maxClusterRadius=maxClusterRadius,
                disableClusteringAtZoom=disableClusteringAtZoom,
                showCoverageOnHover=False,
                zoomToBoundsOnClick=zoomToBoundsOnClick,
                spiderfyOnMaxZoom=spiderfyOnMaxZoom, **kwargs).add_to(self.fgs['photos'])
        else:
            dst = self.fgs['photos']

        # add photos to cluster object
        for idx, photo in self.photos.iterrows():
            xy = photo[self.GPS_INDEX].values.astype(float)

            if groupby is not None:
                gallery = photo[groupby]
            else:
                gallery = None

            popup = ImagePopup(photo.imgur_id, photo.caption, gallery).popup

            icon = BeautifyIcon('camera', 
                                border_width=0,
                                text_color=icon_color, 
                                border_color=icon_color, 
                                background_color='transparent', 
                                inner_icon_style='font-size:20px;padding-top:-1px;')

            tooltip = photo.caption + '\n' + photo.time_shot_utc + photo._name[1] + photo._name[2]

            Marker(xy, popup=popup, 
                   tooltip=tooltip, 
                   icon=icon,
                  ).add_to(dst)

    def add_heatmap_to_map(self, **kwargs):

        # add feature group
        self.fgs['heatmap'] = FeatureGroup('Heatmap', show=False).add_to(self.map)

        # add heatmaps
        for train in self.rail:
            obj = train.get_heatmap(**kwargs)
            obj.add_to(self.fgs['heatmap'])

        for drive in self.land:
            obj = drive.get_heatmap(**kwargs)
            obj.add_to(self.fgs['heatmap'])
            
    def add_video_to_map(self,
                         radius=10, 
                         auto_play=True,
                         **kwargs):


        # add video
        TripSegment(self.pings).get_heatmap_video(
                radius=radius, 
                auto_play=auto_play,
                **kwargs).add_to(self.map)

    def save_map(self, path):
        self.map.save(path)


def find_flights(pings):

    SEMANTIC_GPS_INDEX = ['latitude_geocode', 'longitude_geocode']
    
    flights = [] 
    gps = pings[SEMANTIC_GPS_INDEX].values.astype(float)
    dx = np.array([haversine(*p) for p in zip(gps[:-1], gps[1:])])
    dt = np.array((pings.index.values[1:] - pings.index.values[:-1]).tolist()) / 1e9 / 3600 # hours
    for idx in np.logical_and(dx>250, dx/dt>25).nonzero()[0]:
        flight = FlightSegment(pings.iloc[[idx, idx+1]])
        flights.append(flight)    
    flights = [flight for flight in flights if flight.international or flight.origin.country=='US']
    return flights


def find_drives(pings, transits):
    gps = pings.flattened
    transits = sorted(transits, key=lambda x: x.start)
    drives = [DriveSegment(gps['2019-07-24': '2019-07-31'])]
    for i, transit in enumerate(transits[:-1]):
        drives.append(DriveSegment(gps[transit.stop: transits[i+1].start]))
    drives.append(DriveSegment(gps['2020-02-25': '2020-03-17']))
    return drives


class TripGenerator:
    
    def __init__(self, pings, photos):
        
        self.pings = pings
        self.photos = photos
        
        # find trains/planes/drives
        rail = [
            TrainSegment(pings.pings.loc['SMB'].loc['2019-08-16 05:31:30':'2019-08-16 14:23:57']),
            TrainSegment(pings.pings.loc['CMB'].loc['2019-09-02 11:43:04':'2019-09-02 13:03:54'])]
        air = find_flights(pings.pings.loc['SMB'])
        land = find_drives(pings, rail+air)
        
        self.segments = {
            'air': air,
            'rail': rail,
            'land': land}
        
    def get_trip_segments(self, *trip_ids):
        trip_segments = {'air': [], 'rail': [], 'land': []} 
        for trip_id in trip_ids:
            for segment_type, segments in self.segments.items():
                _ = [trip_segments[segment_type].append(x) for x in segments if trip_id in x.trip_ids]
        return trip_segments
    
    def get_trip_pings(self, *trip_ids):
        match = lambda x: len(set(trip_ids).intersection(set(x))) > 0
        trip_pings = self.pings.flattened[self.pings.flattened.trip_id.apply(match)]
        return trip_pings
    
    def get_trip_photos(self, trip_pings):
        t0, t1 = trip_pings.index.min(), trip_pings.index.max()
        trip_photos = self.photos[self.photos.timestamp.between(t0, t1)]
        return trip_photos
    
    def get_trip(self, *trip_ids):
        segments = self.get_trip_segments(*trip_ids)
        pings = self.get_trip_pings(*trip_ids)
        photos = self.get_trip_photos(pings)
        return Trip(segments, pings, photos)
