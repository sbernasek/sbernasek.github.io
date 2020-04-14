from folium import Popup


class ImagePopup:
    
    def __init__(self, imgur_id, caption=None, gallery=None):
        self.imgur_id = imgur_id
        if caption is None:
            caption = ''
        self.caption = caption
        self._gallery = gallery
        self.popup = Popup(self.html)

    @property
    def gallery(self):

        if self._gallery is None:
            return ''
        else:
            return '="{:s}"'.format(self._gallery)

    @property
    def thumbnail(self):
        return self.build_imgur_url(self.imgur_id, 'b')

    @property
    def img_medium(self):
        return self.build_imgur_url(self.imgur_id, 'm')

    @property
    def img_large(self):
        return self.build_imgur_url(self.imgur_id, 'l')
    
    @property
    def img(self):
        return self.build_imgur_url(self.imgur_id, '')
    
    @staticmethod
    def build_imgur_url(imgur_id, fmt=''):
        return 'https://i.imgur.com/{:s}{:s}.jpg'.format(imgur_id, fmt)
    
    @property
    def html(self):
        return """
        <div>
          <a href="{:s}" target="_blank">
            <img src="{:s}">
          </a>
        </div> 
        """.format(self.img, self.img_large)

    # @property
    # def html(self):
    #     return """
    #     <div class="hovereffect">
    #         <a href="{:s}" data-fancybox{:s} data-caption="{:s}">
    #             <img src="{:s}">
    #         </a>
    #     </div>
    #     """.format(self.img, self.gallery, self.caption, self.img_large)
