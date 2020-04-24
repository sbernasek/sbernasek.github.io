import pandas as pd
from sklearn.cluster import KMeans


class PlaceFinder:
    
    GPS_INDEX = ['latitude', 'longitude']
    
    def __init__(self, data_path='../../data/places.hdf'):
        self.data = pd.read_hdf(data_path, 'data')
        self.data = self.data.drop_duplicates(self.GPS_INDEX)
        self.model = KMeans(n_clusters=len(self.data)).fit(self.xy)
        self.label_to_idx = {label: idx for idx, label in enumerate(self.model.labels_)}
        
    @property
    def xy(self):
        return self.data[self.GPS_INDEX].values
    
    def __call__(self, record):
        label = self.model.predict(record[self.GPS_INDEX].values.reshape(1, -1))[0]
        match_idx = self.label_to_idx[label]
        match = self.data.iloc[match_idx]
        return '{:s}, {:s}'.format(match['name'], match['country'])

