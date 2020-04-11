from os.path import join, exists
from glob import glob
from time import sleep, time
from datetime import datetime
import numpy as np
import pandas as pd
from imgurpython import ImgurClient
from imgurpython.helpers.error import ImgurClientRateLimitError

from modules.utilities import datetime_to_str, str_to_datetime


class Client(ImgurClient):

    INDEX = ['album', 'filename', 'source']

    def __init__(self, 
                 imgur_data_path=None,
                 *args, **kwargs):

        self.imgur_data_path = imgur_data_path
        super().__init__(*args, **kwargs)

        # load imgur data
        if imgur_data_path is not None and exists(imgur_data_path):
            self.load_imgur_data()
        else:
            self.initialize_imgur_data()

        # initialize albums
        self.initialize_albums()

    def save(self, path=None):
        if path is None:
            if self.imgur_data_path is None:
                raise ValueError('No path specified.')
            path = self.imgur_data_path
        self.imgur_data.to_hdf(path, 'data')

    def load_imgur_data(self):
        self.imgur_data = pd.read_hdf(self.imgur_data_path, 'data')

    def initialize_imgur_data(self):
        columns = [
            'album',
            'filename',
            'source',
            'imgur_id',
            'imgur_link',
            'imgur_album_hash',
            'time_uploaded']
        self.imgur_data = pd.DataFrame(columns=columns)
        self.imgur_data = self.imgur_data.set_index(self.INDEX)

    def initialize_albums(self):
        album_hashes = self.get_account_album_ids('sbernasek')
        albums = self.get_account_albums('sbernasek')
        self.album_dict = dict(zip([x.title for x in albums], album_hashes))

    def _upload_image(self, album_hash, metadata_record, sleep_time=1800):

        try:
            config = dict(album=album_hash)
            response = self.upload_from_path(metadata_record.path, 
                                             config=config, anon=False)
            time_uploaded = datetime_to_str(datetime.fromtimestamp(response['datetime']))

            # build imgur data record
            imgur_record = {
                'imgur_id': response['id'],
                'imgur_link': response['link'],
                'imgur_album_hash': album_hash,
                'time_uploaded': time_uploaded
                }

            # compile series
            imgur_record = pd.Series(imgur_record, name=metadata_record._name)

            # save record
            self.imgur_data = self.imgur_data.append(imgur_record, ignore_index=False)

        except ImgurClientRateLimitError:
            print('Rate limit exceeded.')
            sleep(sleep_time)
            self._upload_image(album_hash, metadata_record, sleep_time)

    def upload_image(self, album_hash, metadata_record):

        # if image exists, delete it
        if self.imgur_data.index.isin([metadata_record._name]).any():
            imgur_record = self.imgur_data.loc[metadata_record._name]
            response = self.delete_image(imgur_record['imgur_id'])
            self.imgur_data.drop(metadata_record._name, inplace=True)

        # upload new one
        self._upload_image(album_hash, metadata_record)

    def create_album(self, title):
        fields = dict(title=title, privacy='hidden')
        response = super().create_album(fields)
        self.album_dict[title] = response['id']

    def upload_images(self, metadata_records, delay=60):

        for album, records in metadata_records.groupby('album'):

            start = time()
            print('Starting {:s}'.format(album))

            # create album
            if album not in self.album_dict.keys():
                self.create_album(album)

            # add all images in album
            for i, (idx, record) in enumerate(records.iterrows()):
                self.upload_image(self.album_dict[album], record)
                print('{:d}/{:d}'.format(i+1, len(records)))

                # pause to avoid rate limiting
                sleep(delay)

            print('Completed {:s} in {:0.2f} s'.format(album, time()-start))

        # update metadata
        self.save()

    def upload_new_images(self, photo_metadata, delay=60):

        def is_later(x):
            if type(x.time_uploaded) == float and np.isnan(x.time_uploaded):
                return True
            else:
                return str_to_datetime(x.time_uploaded) < str_to_datetime(x.time_rendered)
        
        # select images that have been rendered since last upload
        records = photo_metadata[photo_metadata.join(self.imgur_data).apply(is_later, axis=1)]

        self.upload_images(records, delay=delay)
