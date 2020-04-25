import gpxpy
import gpxpy.gpx
import altair as alt
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans

from folium import PolyLine, Popup, Marker, VegaLite
from folium.plugins import BeautifyIcon


class Track:
    
    def __init__(self, segments):
        points = [self.point_to_dict(x) for x in segments.points]
        data = pd.DataFrame(points)
        self.data = data.set_index('timestamp')
        
    @staticmethod
    def point_to_dict(pt):
        return {
            'timestamp': pt.time,
            'latitude': pt.latitude,
            'longitude': pt.longitude,
            'elevation': pt.elevation}


class ActivityIO:
    
    GPS_INDEX = ['latitude', 'longitude']
    
    def __init__(self, activity_id, data, metadata):
        self.data = data        
        self.activity_id = activity_id
        self.name = metadata['name']
        self.type = metadata['type']
        self.centroid = metadata['centroid']
        self.max_speed = metadata['max_speed']
        self.moving_time = metadata['moving_time']
        self.moving_distance = metadata['moving_distance']
        self.bbox = metadata['bbox']
        self.downhill = metadata['downhill']
        self.uphill = metadata['uphill']
        self._start = metadata['start']
        self._stop = metadata['stop']

    @property
    def metadata(self):
        return {k: v for k,v in self.__dict__.items() if k!='data'}
        
    @classmethod
    def from_cache(cls, activity_id, GPX_CACHE, GPX_METADATA_CACHE):
        data = GPX_CACHE.loc[activity_id]
        metadata = GPX_METADATA_CACHE.loc[activity_id]
        return cls(metadata.name, data, metadata)
    
    @classmethod
    def from_gpx(cls, gpx_path):
        
        metadata = {}
        
        activity_id = gpx_path.split('/')[-1].strip('.gpx')
        metadata['activity_id'] = activity_id
        
        track = cls.load_track_from_gpx(gpx_path)
        metadata['name'] = track.name
        metadata['type'] = track.type
        
        center = track.get_center()
        metadata['centroid'] = (center.latitude, center.longitude)

        moving = track.get_moving_data()
        metadata['max_speed'] = moving.max_speed
        metadata['moving_time'] = moving.moving_time
        metadata['moving_distance'] = moving.moving_distance
            
        bounds = track.get_bounds()
        metadata['bbox'] = (bounds.min_latitude, bounds.min_longitude, bounds.max_latitude, bounds.max_longitude)
        
        updown = track.get_uphill_downhill()
        metadata['downhill'] = updown.downhill
        metadata['uphill'] = updown.uphill
        
        timebounds = track.get_time_bounds()
        metadata['start'] = timebounds.start_time
        metadata['stop'] = timebounds.end_time
        
        data = Track(track.segments[0]).data
        data['activity_id'] = metadata['activity_id']
        
        return cls(activity_id, data, metadata)
                
    @property
    def pings(self):
        return self.data[self.GPS_INDEX]
    
    @staticmethod
    def load_track_from_gpx(gpx_path):
        with open(gpx_path, 'r') as gpx_file:
            gpx = gpxpy.parse(gpx_file)
        assert len(gpx.routes) == 0, 'Routes found.'
        assert len(gpx.waypoints) == 0, 'Waypoints found.'
        assert len(gpx.tracks) == 1, 'Additional tracks found.'        
        track = gpx.tracks[0]
        return track


class Activity(ActivityIO):

    @property
    def finish(self):
        return self.pings.values[-1]
    
    @property
    def start(self):
        return self._start.tz_localize(None)

    @property
    def stop(self):
        return self._stop.tz_localize(None)

    def within(self, *timespan):
        start, stop = timespan
        if self.start < start or self.stop > stop:
            return False
        else:
            return True

    @property
    def is_skiing(self):
        return 'skiing' in self.caption.lower()

    @property
    def is_hiking(self):
        return 'hiking' in self.caption.lower()
    
    @staticmethod
    def parse_activity_name(s):
        s = s.replace('Running', '')
        s = s.replace('Other', '')
        s = s.replace('Skiing', '')
        s = s.replace('Hiking', '')
        s = s.replace('Hike', '')
        s = s.replace('ERROR (part 1)', '')
        s = s.replace('County', '')
        s = s.replace('Contra Costa', 'Lafayette')
        s = s.replace('Dacorum', 'Berkhamsted')
        s = s.replace('Alpine Meadows', 'Alpine')
        return s.strip()

    @property
    def semantic(self):
        return self.parse_activity_name(self.name)
    
    @staticmethod
    def parse_activity(s):
        activities = {
            'running': 'Running',
            'street_running': 'Running',
            'hiking': 'Hiking',
            'resort_skiing_snowboarding_ws': 'Skiing',
            'strength_training': 'Lifting'}
        return activities[s]

    @property
    def activity(self):
        return self.parse_activity(self.type)

    @property
    def caption(self):
        caption_strings = {
            'running': 'Running in {:s}',
            'street_running': 'Running in {:s}',
            'hiking': 'Hiking {:s}',
            'resort_skiing_snowboarding_ws': 'Skiing at {:s}',
            'strength_training': 'Doing {:s}'}

        s = caption_strings[self.type].format(self.semantic)
        s += ' on {:s}'.format(self.start.strftime('%D'))
        return s

    def build_chart(self, width=400, height=225, scheme='tealblues'):
    
        data = self.data.elevation.resample('1T').mean().interpolate().reset_index()
        data['Elevation (ft)'] = data.elevation * 3.28084
        data['Time Elapsed (hr)'] = (data.timestamp - data.timestamp[0]).apply(lambda x: x.total_seconds()/3600)

        line_kw = dict(strokeWidth=2, interpolate='natural', color='firebrick')

        # create chart
        chart = alt.Chart(data, width=width, height=height).mark_line(**line_kw).encode(
                    x=alt.X('Time Elapsed (hr)'),
                    y=alt.Y('Elevation (ft)', scale=alt.Scale(zero=False))
                ).configure_axis(grid=False
                ).configure_view(strokeWidth=0
                ).properties(title=self.name)

        chart.configure_title(
            fontSize=18,
            )
        
        return chart

    @property
    def icon_name(self):
        if self.activity == 'Skiing':
            return 'info-circle'
        elif self.activity == 'Hiking':
            return 'info-circle'
        else:
            return 'info-circle'

    def get_marker(self, 
                   width=450,
                   height=250,
                   icon_color='#966fd6', 
                   chart_kw={}):

        chart = self.build_chart(width=width-75, height=height-25, **chart_kw)

        popup = Popup(max_width=width).add_child(
                    VegaLite(chart.to_json(), width=width, height=height)) 

        icon_kw = dict(
            icon_shape='circle',
            border_width=0,
            text_color='white', 
            border_color='white', 
            background_color='green', 
            inner_icon_style='font-size:11px; padding-top: 1px;')

        icon = BeautifyIcon('line-chart', **icon_kw)

        location = self.data.iloc[0][['latitude', 'longitude']].values

        marker = Marker(
            location=location,
            icon=icon,
            tooltip=self.semantic,
            popup=popup)

        return marker

    def get_line(self, **kwargs):
        return PolyLine(self.pings.values, 
                        tooltip=self.caption, 
                        **kwargs)



gpx_data_dirpath = '../../data/activities/gpx'

GPX_CACHE_PATH = '../../data/activities/cache.hdf'
GPX_CACHE = pd.read_hdf(GPX_CACHE_PATH, 'data')
GPX_CACHE = GPX_CACHE.set_index(['activity_id', 'timestamp'])

GPX_METADATA_CACHE = pd.read_hdf(GPX_CACHE_PATH, 'metadata')
GPX_METADATA_CACHE['day_location'] = GPX_METADATA_CACHE.name.apply(Activity.parse_activity_name)
GPX_METADATA_CACHE['activity'] = GPX_METADATA_CACHE.type.apply(Activity.parse_activity)


SKI_DAYS_GPX = pd.read_hdf(GPX_CACHE_PATH, 'skiing').set_index(['activity_id', 'location', 'timestamp'])

def filter_activities(timespans, types=None):

    global GPX_CACHE
    global GPX_METADATA_CACHE

    activity_ids = GPX_CACHE.index.get_level_values(0).unique().values

    activities = []
    for activity_id in activity_ids:
        activity = Activity.from_cache(activity_id, GPX_CACHE, GPX_METADATA_CACHE)
        
        if timespans is not None:
            for timespan in timespans:
                if activity.within(*timespan):
                    if types is None or activity.activity in types:
                        activities.append(activity)
                        break
        else:
            activities.append(activity)

    return activities


def split_multiresort(gb):
    
    global GPX_METADATA_CACHE

    activity_id = gb.index.get_level_values(0)[0]
    metadata = GPX_METADATA_CACHE.loc[activity_id]
    
    if '/' in metadata.day_location:
        cluster_ids = KMeans(2).fit_predict(gb.latitude.values.reshape(-1, 1))
        locations = metadata.day_location.split('/')
        if cluster_ids[0] == 0:
            labeler = np.vectorize(dict(enumerate(locations)).get)
        else:
            labeler = np.vectorize(dict(enumerate(locations[::-1])).get)    

        labels = labeler(cluster_ids)
    else:
        labels = [metadata.day_location for x in range(len(gb))]

    return pd.DataFrame(labels, index=gb.index)


def get_elevation_gain(x):
    dz = x.elevation.diff().fillna(0).values
    dz[dz<0] = 0
    return pd.DataFrame(np.cumsum(dz), index=x.index)
              
def get_time_elapsed(x):
    timestamps = x.index.get_level_values(2).values
    return pd.DataFrame((timestamps - timestamps[0]), index=x.index)


# process ski days
# SKI_DAYS_METADATA = GPX_METADATA_CACHE[GPX_METADATA_CACHE.activity=='Skiing']
# SKI_DAYS_GPX = GPX_CACHE.loc[SKI_DAYS_METADATA.index]
# SKI_DAYS_GPX['location'] = SKI_DAYS_GPX.groupby(level=0).apply(split_multiresort)
# SKI_DAYS_GPX = SKI_DAYS_GPX.reset_index().set_index(['activity_id', 'location', 'timestamp'])
# SKI_DAYS_GPX['time_elapsed'] = SKI_DAYS_GPX.groupby(level=(0, 1)).apply(get_time_elapsed)
# SKI_DAYS_GPX['elevation_gain'] = SKI_DAYS_GPX.groupby(level=(0, 1)).apply(get_elevation_gain)
# SKI_DAYS_GPX.reset_index().to_hdf(GPX_CACHE_PATH, 'skiing')


def build_ski_chart(location, data, width=400, height=225, scheme='viridis'):

    line_kw = dict(strokeWidth=2)
    legend_kw = dict(title="Date", orient="top-left", offset=10, padding=0)
    color_kw = dict(scale=alt.Scale(scheme=scheme), legend=alt.Legend(**legend_kw))

    # create chart
    chart = alt.Chart(data, width=width, height=height).mark_line(**line_kw).encode(
            x=alt.X('time_elapsed_hours', axis=alt.Axis(title='Time Elapsed (h)')),
            y=alt.Y('elevation_gain_ft', axis=alt.Axis(title='Vertical Feet')),
            color=alt.Color('date', **color_kw),
            ).configure_axis(
                grid=False
            ).configure_view(
                strokeWidth=0
            ).properties(title='Ski days in {:s}'.format(location))

    chart.configure_title(
        fontSize=18,
        )

    return chart


def build_ski_marker(location, data, 
               width=475,
               height=250,
               icon_color='#966fd6', 
               chart_kw={}):
        
        
        centroid = data[['latitude', 'longitude']].iloc[0].values
        tooltip = 'Skiing in {:s}'.format(location)   
        chart = build_ski_chart(location, data, width=width-75, height=height-25, **chart_kw)
        
        popup = Popup(max_width=width).add_child(
                    VegaLite(chart.to_json(), width=width, height=height)) 

        icon_kw = dict(
            icon_shape='circle',
            border_width=0,
            text_color='white', 
            border_color='white', 
            background_color='black', 
            inner_icon_style='font-size:11px; padding-top: 1px;')

        icon = BeautifyIcon('line-chart', **icon_kw)

        marker = Marker(
            location=centroid,
            icon=icon,
            tooltip=tooltip,
            popup=popup)

        return marker


# # compile resampled ski days
# SKI_DAYS_GPX['time_elapsed'] = SKI_DAYS_GPX.time_elapsed.apply(lambda x: x.total_seconds())
# SKI_DAYS_GPX_RESAMPLED = SKI_DAYS_GPX.unstack(level=[0,1]).resample('10T').mean().stack(level=[2,1]).swaplevel(2,0)
# SKI_DAYS_GPX_RESAMPLED['date'] = GPX_METADATA_CACHE.loc[SKI_DAYS_GPX_RESAMPLED.index.get_level_values(0)].start.apply(lambda x: x.strftime('%D')).values
# SKI_DAYS_GPX_RESAMPLED['time_elapsed_hours'] = SKI_DAYS_GPX_RESAMPLED.time_elapsed / 3600
# SKI_DAYS_GPX_RESAMPLED['elevation_gain_ft'] = SKI_DAYS_GPX_RESAMPLED.elevation_gain * 3.28084
# SKI_DAYS_GPX_RESAMPLED.reset_index().to_hdf(GPX_CACHE_PATH, 'skiing_resampled')

SKI_DAYS_GPX_RESAMPLED = pd.read_hdf(GPX_CACHE_PATH, 'skiing_resampled').set_index(['activity_id', 'location', 'timestamp'])
