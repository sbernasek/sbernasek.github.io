from folium import Popup
from branca.element import IFrame


class ImagePopup:
    
    def __init__(self, imgur_id, 
                 caption=None, 
                 aspect=None,
                 gallery=None,
                 size=300):
        self.imgur_id = imgur_id
        if caption is None:
            caption = ''
        self.caption = caption
        self.aspect = 1/aspect
        self._gallery = gallery

        options = dict(
            #autoPanPadding=(200, 200),
            autoPan=False,
            className='smb-map-popup'
        )

        size_str = '{:d}px'.format(int(size))

        if gallery is None:

            if self.aspect > 1:
                width = '{:d}px'.format(int(size/self.aspect))
                iframe = IFrame(html=self.html, width=width, height=size_str)
            else:
                iframe = IFrame(html=self.html, width=size_str, ratio='{:0.0%}'.format(self.aspect))
            
            self.popup = Popup(iframe, **options)
        else:
            self.popup = Popup(self.html_gallery, **options)

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
        <div class="smb-map-image-container">
            <img src="{:s}" style="width:100%; height:100%;">
        </div> 
        """.format(self.img, self.img_large)

    # @property
    # def html(self):
    #     return """
    #     <div class="smb-map-image-container">
    #         <a href="{:s}" data-fancybox="HORSE" data-caption="{:s}">
    #             <img src="{:s}" style="width:98%; height:98%;">
    #         </a>
    #     </div>
    #     """.format(self.img, self.caption, self.img_large)

    @property
    def html_gallery(self):
        return """
        <div class="smb-map-image-container">
            <a href="{:s}" data-fancybox{:s} data-caption="{:s}" target="_blank">
                <img src="{:s}" style="width:100%; height:100%;">
            </a>
        </div>
        """.format(self.img, self.gallery, self.caption, self.img_large)
