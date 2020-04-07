from os.path import join
import pystache


class ImageHtmlTemplate(object):

    def __init__(self, url, caption=None, gps=None, place_id=None):
        self._url = url
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
        return self._url

    def caption(self):
        return self._caption

    def hyperlink(self):
        return self._hyperlink


class PostTemplate(object):

    def __init__(self, title, records, cover=None, subtitle=None):
        self._title = title
        self._subtitle = subtitle
        self._cover = cover
        self.records = records
        self.renderer = pystache.Renderer()

    def title(self):
        return self._title

    def subtitle(self):
        return self._subtitle

    def cover(self):
        if self.cover is None:
            return self.records.iloc[0].imgur_link
        else:
            return self._cover

    def images(self):
        html_strings = self.records.apply(self.render_image_html, axis=1)
        return '\n\n'.join(html_strings)

    def render_image_html(self, record):

        gps, place_id = None, None
        if record.distance_to_semantic < 5:
            place_id = record.place_id
        if record.distance_to_semantic < 15:
            gps = [record.latitude_used, record.longitude_used]

        image = ImageHtmlTemplate(record.imgur_link, 
                                  caption=record.caption,
                                  gps=gps,
                                  place_id=place_id)

        return self.renderer.render(image)


class Post:
    
    posts_dir = '../_posts' 
    
    def __init__(self, filename, title, records, cover=None):
        self.filepath = join(self.posts_dir, '{:s}.md'.format(filename))
        template = PostTemplate(title, records, cover=cover)
        self.post = pystache.Renderer().render(template)
        
    def write(self):
        with open(self.filepath, 'w') as file:
            file.write(self.post)
