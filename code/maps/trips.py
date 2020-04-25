import numpy as np
import pandas as pd
from functools import reduce
from operator import add
from sklearn.cluster import MeanShift
from folium import Map, TileLayer, Icon
from folium import FeatureGroup, LayerControl, Marker
from folium.plugins import MarkerCluster, BeautifyIcon, FeatureGroupSubGroup

from modules.utilities import haversine
from maps.popup import ImagePopup
from maps.maps import FoliumMap
from maps.segments import TripSegment
from maps.segments import TrainSegment, FlightSegment, DriveSegment


class Trip:

    GPS_INDEX = ['latitude', 'longitude']

    def __init__(self, segments, pings, photos, trip_ids=None):
        self.segments = segments
        self.pings = pings
        self.photos = photos
        self.trip_ids = trip_ids

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
                  location=None,
                  zoom_start=5,
                  max_zoom=15,
                  **kwargs):

        if location is None:
            location = self.centroid

        # create map
        m = Map(width='100%', height='100%',
                tiles='cartodbpositron',
                location=location, 
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
        flight_color='darkred',
        train_color='green',
        drive_color='black',
        weight=3,
        show=False,
        drive_kwargs={}):

        # add feature group
        if self.trip_ids is not None:
            for trip_id in self.trip_ids:
                self.fgs[trip_id] = FeatureGroup(trip_id, show=show).add_to(self.map)

        # add start/finish
        icon_kw = dict(icon_shape='marker',
                        border_width=2,
                        text_color='black', 
                        border_color='black', 
                        background_color='white', 
                        inner_icon_style='font-size:14px; padding-top:-1px;')
        start, finish = self.bounds
        
        # add segments
        arrived = {k: False for k in self.trip_ids}
        for flight in self.air:

            for trip_id in flight.trip_ids:
                
                if trip_id not in self.fgs.keys():
                    continue

                if not arrived[trip_id] or trip_id == 'Return Flights':

                    arrived[trip_id] = True
                    for leg in flight.legs:

                        obj = leg.get_line(
                          color=flight_color, 
                          weight=weight, 
                          opacity=0.5).add_to(self.fgs[trip_id])

                        if leg.is_connection:
                            tooltip = 'Layover in {:s}'.format(leg.destination_str)
                        else:
                            tooltip = 'Arriving from {:s}'.format(leg.origin_str)

                        # arrival icon
                        _ = Marker(leg.destination[flight.GPS_INDEX].values, 
                               icon=BeautifyIcon('arrow-down', **icon_kw),
                               tooltip=tooltip,
                               ).add_to(self.fgs[trip_id])

                else:

                    # departure icon
                    _ = Marker(flight.origin[flight.GPS_INDEX].values, 
                               icon=BeautifyIcon('plane', **icon_kw),
                               tooltip='Departing to {:s}'.format(flight.destination_str),
                               ).add_to(self.fgs[trip_id])

        for train in self.rail:
            for trip_id in train.trip_ids:
                if trip_id not in self.fgs.keys():
                    continue
                obj = train.get_antpath(color=train_color, weight=weight, opacity=0.5)
                obj.add_to(self.fgs[trip_id])
            
        for drive in self.land:

            for trip_id in drive.trip_ids:
                if trip_id not in self.fgs.keys():
                    continue

                options = {'smoothFactor': 10}
                try:
                    obj = drive.get_antpath(color=drive_color, 
                                            weight=weight, 
                                            options=options,
                                            **drive_kwargs)
                    obj.add_to(self.fgs[trip_id])
                except:
                    print('No drive segments found in {:s}'.format(drive.caption))

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

            popup = ImagePopup(photo.imgur_id, 
                               caption=photo.caption, 
                               aspect=photo.image_aspect,
                               gallery=gallery).popup

            icon = BeautifyIcon('camera', 
                                border_width=0,
                                text_color=icon_color, 
                                border_color=icon_color, 
                                background_color='transparent', 
                                inner_icon_style='font-size:20px;padding-top:-1px;')

            Marker(xy, popup=popup, 
                   tooltip=photo.caption, 
                   icon=icon,
                  ).add_to(dst)

    def add_activities(self, activities,
        line_color='purple',
        show=True):

        self.fgs['activities'] = FeatureGroup('Hiking/Skiing', show=show).add_to(self.map)
            
        # add activities to map
        for activity in activities:
            obj = activity.get_line(line_color=line_color, weight=1).add_to(self.fgs['activities'])

            if activity.is_hiking:
                obj = activity.get_marker().add_to(self.fgs['activities'])

    def add_heatmap_to_map(self, show=False, **kwargs):

        # add feature group
        self.fgs['heatmap'] = FeatureGroup('Heatmap', show=show).add_to(self.map)

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

    # SEMANTIC_GPS_INDEX = ['latitude_geocode', 'longitude_geocode']
    
    # flights = [] 
    # gps = pings[SEMANTIC_GPS_INDEX].values.astype(float)
    # dx = np.array([haversine(*p) for p in zip(gps[:-1], gps[1:])])
    # dt = np.array((pings.index.values[1:] - pings.index.values[:-1]).tolist()) / 1e9 / 3600 # hours
    # for idx in np.logical_and(dx>250, dx/dt>25).nonzero()[0]:
    GPS_INDEX = ['latitude', 'longitude']
    gps = pings[GPS_INDEX].values.astype(float)
    dx = np.array([haversine(*p) for p in zip(gps[:-1], gps[1:])])
    dt = np.array((pings.index.values[1:] - pings.index.values[:-1]).tolist()) / 1e9 / 3600 # hours

    flights = [] 
    for idx in np.logical_and(dx > 250, (dx/dt)>50).nonzero()[0]:
        flight = FlightSegment(pings.iloc[[idx, idx+1]])
        flights.append(flight)    
    flights = [flight for flight in flights if flight.international or flight.origin.country=='US']
    return flights


def find_drives(pings, transits):
    gps = pings.flattened
    transits = sorted(transits, key=lambda x: x.start)
    drives = [DriveSegment(gps['2019-07-24': '2019-08-01'])]
    for i, transit in enumerate(transits[:-1]):
        # skip segments < 24h
        if float(transits[i+1].start - transit.stop)/1e9 < (3600*48):
            continue
        drives.append(DriveSegment(gps[transit.stop: transits[i+1].start]))
    drives.append(DriveSegment(gps['2020-02-25': '2020-03-18']))
    return drives


class TripGenerator:
    
    def __init__(self, pings, photos):
        
        self.pings = pings
        self.photos = photos
        
        # find trains/planes/drives
        rail = [
            TrainSegment(pings.pings.loc['SMB'].loc['2019-08-16 05:31:30':'2019-08-16 14:23:57']),
            TrainSegment(pings.pings.loc['CMB'].loc['2019-09-02 11:43:04':'2019-09-02 13:03:54']),
            TrainSegment(pings.flattened.loc['2019-09-25 14:31:48': '2019-09-25 17:50:00']),
            TrainSegment(pings.pings.loc['CMB'].loc['2019-09-30 12:00:00': '2019-09-30 17:50:00'])
            ]
        air = find_flights(pings.flattened)
        land = find_drives(pings, rail+air)
        
        self.segments = {
            'air': air,
            'rail': rail,
            'land': land}

        self.add_connections()
    
    @property
    def ordered_segments(self):
        return sorted(reduce(add, list(self.segments.values())), key=lambda x: x.start)

    def get_trip_segments(self, *trip_ids, timespans=None):
        trip_segments = {'air': [], 'rail': [], 'land': []} 
        for segment_type, segments in self.segments.items():
            for segment in segments:
                if len(set(segment.trip_ids).intersection(set(trip_ids))) > 0:

                    if timespans is not None:
                        for timespan in timespans:
                            if segment.within(timespan):
                                trip_segments[segment_type].append(segment)
                                break
                    else:
                        trip_segments[segment_type].append(segment)

        return trip_segments
    
    def add_connections(self):
        r_segments = self.ordered_segments[::-1]
        for idx, flag in enumerate(np.diff(np.array([x.is_flight for x in r_segments], dtype=int))):
            if flag == 1:
                arriving_flight = r_segments[idx+1]
                on_segment = True
            elif flag == 0 and on_segment:
                connecting_flight = r_segments[idx+1]
                connecting_flight.is_connection = True
                arriving_flight.add_connection(connecting_flight)        
            else:
                arriving_flight = None
                on_segment = False

    def get_trip_pings(self, *trip_ids, timespans=None):
        match = lambda x: len(set(trip_ids).intersection(set(x))) > 0
        trip_pings = self.pings.flattened[self.pings.flattened.trip_id.apply(match)]

        if timespans is not None:
            dfs = []
            for timespan in timespans:
                start, stop = timespan
                dfs.append(trip_pings.loc[start: stop])
            trip_pings = pd.concat(dfs)

        return trip_pings
    
    def get_trip_photos(self, trip_pings, timespans=None):
        t0, t1 = trip_pings.index.min(), trip_pings.index.max()
        trip_photos = self.photos[self.photos.timestamp.between(t0, t1)]

        if timespans is not None:
            dfs = []
            for timespan in timespans:
                dfs.append(trip_photos[trip_photos.timestamp.between(*timespan)])
            trip_photos = pd.concat(dfs)

        return trip_photos
    
    def get_trip(self, *trip_ids, timespans=None):
        segments = self.get_trip_segments(*trip_ids, timespans=timespans)
        pings = self.get_trip_pings(*trip_ids, timespans=timespans)
        photos = self.get_trip_photos(pings, timespans=timespans)

        return Trip(segments, pings, photos, trip_ids=trip_ids)
