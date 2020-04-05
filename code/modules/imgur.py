from os.path import join, exists
from glob import glob
from time import sleep
import pandas as pd
from imgurpython import ImgurClient
from imgurpython.helpers.error import ImgurClientRateLimitError

from .jpeg import JPEG_Metadata


class Client(ImgurClient):
    
    metadata_path = './data/metadata.hdf'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initialize()
    
    def initialize_metadata(self):
        if exists(self.metadata_path):
            self.metadata = pd.read_hdf(self.metadata_path, key='data')

        else:
            columns = [
                'path',
                'filename',
                'time_shot',
                'time_rendered',
                'gps',
                'model',
                'album',
                'album_path',
                'album_hash',
                'imgur_link',
                'imgur_id']

            self.metadata = pd.DataFrame(columns=columns)

    def initialize(self):
        self.initialize_metadata()
        album_hashes = self.get_account_album_ids('sbernasek')
        albums = self.get_account_albums('sbernasek')
        self.album_dict = dict(zip([x.title for x in albums], album_hashes))
        self.uploads = []

    def upload_image(self, path, album):
        album_hash = self.album_dict[album]
        config = dict(album=album_hash)
        response = self.upload_from_path(path, config=config, anon=False)

        # build metadata record
        metadata = JPEG_Metadata(path).to_record()
        metadata['album'] = album
        metadata['album_path'] = path.rsplit('/', maxsplit=1)[0]
        metadata['album_hash'] = album_hash
        metadata['imgur_link'] = response['link']
        metadata['imgur_id'] = response['id']

        # save record
        self.metadata = self.metadata.append(metadata, ignore_index=True)

    def upload_album(self, path, title, delay=20):

        # create album
        if title not in self.album_dict.keys():
            self.create_album(title)

        # upload images to album
        img_paths = glob(join(path, '*.j*'))
        for i, img_path in enumerate(img_paths):

            if img_path in self.metadata.path.values:
                continue

            try:
                self.upload_image(img_path, title)
                print('{:d}/{:d} complete'.format(i+1, len(img_paths)))
            except ImgurClientRateLimitError:
                print('Album:', title)
                print('Rate limit exceeded on Image #{:d}'.format(i))
                sleep(1800)
                self.upload_album(path, title, delay=delay)
            
            # pause to avoid rate limiting
            sleep(delay)

        # update metadata
        self.metadata.to_hdf(self.metadata_path, key='data')

    def create_album(self, title):
        fields = dict(title=title, privacy='hidden')
        response = super().create_album(fields)
        self.album_dict[title] = response['id']
