from sklearn.cluster import KMeans
import reverse_geocoder
import pandas as pd 


class Pings:
    
    GPS_INDEX = ['latitude', 'longitude']
    
    def __init__(self, pings, rounding=2):

        self._pings = pings.set_index(['owner', pings.index])
        self.rounding = rounding
        samples, weights = self._consolidate(pings, rounding=rounding)
        self.samples = samples
        self.weights = weights
    
    @property
    def gps(self):
        return self._pings[self.GPS_INDEX].values

    @property
    def pings(self):
        return self._pings.join(self.locations, rsuffix='_geocode')

    @property
    def flattened(self):
        return self.pings.droplevel(0).sort_index()
    
    @property
    def foo(self):
        return self._foo
    
    @property
    def num_pings(self):
        return len(self._pings)

    @property
    def num_consolidated_pings(self):
        return self.samples.shape[0]

    @property
    def compression(self):
        return self.num_consolidated_pings / self.num_pings
    
    @property
    def centroids(self):
        return self.model.cluster_centers_
    
    @property
    def sample_labels(self):
        return self.model.predict(self.samples)

    def _label(self, pings):
        return self.model.predict(pings[self.GPS_INDEX].values)

    def _geocode(self, pings):
        geocode_ids = self._label(pings)
        locations = self.geocodes.loc[geocode_ids].set_index(pings.index)
        locations['geocode_id'] = geocode_ids
        return locations

    def geocode(self):
        self.locations = self._geocode(self._pings)

    @staticmethod
    def _consolidate(pings, rounding=2):
        df = pings[Pings.GPS_INDEX].round(rounding).groupby(Pings.GPS_INDEX)['latitude'].count()
        samples = df.index.to_frame().values
        weights = df.values/df.values.sum()
        return samples, weights
    
    @staticmethod
    def _cluster(samples, weights=None, n_clusters=100):    
        return KMeans(n_clusters=n_clusters).fit(samples, sample_weight=weights)
    
    def cluster(self, use_weights=True, n_clusters=100):

        if use_weights:
            weights = self.weights
        else:
            weights = None

        self.model = self._cluster(self.samples, 
                                   weights, 
                                   n_clusters=n_clusters)

    def build_geocodes(self):
        gps_tuples = [tuple(xy) for xy in self.centroids]
        geocodes = reverse_geocoder.search(gps_tuples) 
        columns= ['latitude','longitude', 'city', 'state', 'region', 'country']
        geocodes = pd.DataFrame(geocodes)
        geocodes.columns = columns
        self.geocodes = geocodes

    def label_timespans(self, attr, labels):

        """
        attr (str) - name of attribute
        labels (dict) - { attr_value: (t0, t1) }
        """

        self._pings[attr] = [[] for _ in range(len(self._pings))]
        for label, (t0, t1) in labels.items():
            after_start = self._pings.index.get_level_values(1) >= t0
            before_end = self._pings.index.get_level_values(1) <= t1

            self._pings.loc[after_start&before_end, attr].apply(lambda x: x.append(label))

    # def label_timespans(self, attr, labels):

    #     """
    #     attr (str) - name of attribute
    #     labels (dict) - { attr_value: (t0, t1) }
    #     """

    #     self._pings[attr] = None
    #     for label, (t0, t1) in labels.items():
    #         after_start = self._pings.index.get_level_values(1) >= t0
    #         before_end = self._pings.index.get_level_values(1) <= t1
    #         self._pings.loc[after_start&before_end, attr] = label

