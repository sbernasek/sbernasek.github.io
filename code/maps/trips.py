import pandas as pd
from sklearn.cluster import MeanShift
from folium import Map, TileLayer, Icon
from folium import FeatureGroup, LayerControl, Marker
from folium.plugins import MarkerCluster, BeautifyIcon

from maps.popup import ImagePopup
from maps.maps import FoliumMap
from maps.segments import TripSegment


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
                  zoom_start=5):

        # create map
        m = Map(width='100%', height='100%',
                tiles='cartodbpositron',
                location=self.centroid, 
                zoom_start=zoom_start)

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
            obj = drive.get_antpath(color=drive_color, weight=weight)
            obj.add_to(self.fgs['land'])

    def add_photos_to_map(self, 
                          clustered=True,
                          maxClusterRadius=20,
                          icon_color='#b3334f',
                          groupby=None):

        # add feature group
        self.fgs['photos'] = FeatureGroup('Photos', show=True).add_to(self.map)

        # create photo cluster object
        if clustered:
            dst = MarkerCluster(
                maxClusterRadius=maxClusterRadius,
                showCoverageOnHover=False,
                disableClusteringAtZoom=11,
                zoomToBoundsOnClick=True,
                spiderfyOnMaxZoom=True).add_to(self.fgs['photos'])
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

            tooltip = photo.caption
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
