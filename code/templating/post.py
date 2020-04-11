from os.path import join
import numpy as np
import pystache


def build_imgur_url(imgur_id, fmt=''):
    return 'https://i.imgur.com/{:s}{:s}.jpg'.format(imgur_id, fmt)


class ImageHtmlTemplate(object):

    def __init__(self, imgur_id, is_horizontal,
                 caption=None, 
                 gps=None, 
                 place_id=None):
        self.imgur_id = imgur_id
        self.is_horizontal = is_horizontal
        if caption is None:
            caption = 'PLACEHOLDER_CAPTION'
        self._caption = caption
        self._hyperlink = self.build_hyperlink(gps)

    @staticmethod
    def build_hyperlink(gps, place_id=None):
        if gps is None:
            return ''
        elif None in gps:
            return ''
        else:
            query = 'https://www.google.com/maps/search/?api=1&query={:3.7f},{:3.7f}'.format(*gps)
            if place_id is not None:
                query += '&query_place_id={:s}'.format(place_id)
            return 'href="{:s}"'.format(query)

    def url(self):
        return build_imgur_url(self.imgur_id)

    def url_square(self):
        return build_imgur_url(self.imgur_id, 'b')

    def url_medium(self):
        return build_imgur_url(self.imgur_id, 'm')

    def url_large(self):
        return build_imgur_url(self.imgur_id, 'l')

    def url_huge(self):
        return build_imgur_url(self.imgur_id, 'h')

    def grid_item_class(self):
        if self.is_horizontal:
            return 'grid-item--horizontal'
        else:
            return 'grid-item--vertical'

    def caption(self):
        return self._caption

    def hyperlink(self):
        return self._hyperlink


class PostTemplate(object):

    def __init__(self, title, records, cover_id=None, subtitle=None):
        self._title = title
        self._subtitle = subtitle
        self._cover_id = cover_id
        self.records = records
        self.renderer = pystache.Renderer()

    def title(self):
        return self._title

    def subtitle(self):
        return self._subtitle

    @property
    def cover_id(self):
        if self._cover_id is None:
            return self.records.iloc[0].imgur_id
        else:
            return self._cover_id

    def cover_url(self):
        return build_imgur_url(self.cover_id, 'l')

    def images(self):
        html_strings = self.records.apply(self.render_image_html, axis=1)
        return '\n\n'.join(html_strings)

    def render_image_html(self, record):

        gps, place_id = None, None

        if type(record.place_id) == str:
            place_id = record.place_id

        if not np.isnan(record.latitude):
            gps = [record.latitude, record.longitude]

        image = ImageHtmlTemplate(record.imgur_id, 
                                  record.is_horizontal,
                                  caption=record.caption,
                                  gps=gps,
                                  place_id=place_id)

        return self.renderer.render(image)


class Post:
    
    posts_dir = '../_posts' 
    
    def __init__(self, filename, title, records, cover_id=None):
        self.filepath = join(self.posts_dir, '{:s}.md'.format(filename))
        template = PostTemplate(title, records, cover_id=cover_id)
        self.post = pystache.Renderer().render(template)
        
    def write(self):
        with open(self.filepath, 'w') as file:
            file.write(self.post)
