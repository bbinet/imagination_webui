import json
import urllib2
from operator import itemgetter

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.settings import asbool


@view_config(route_name='index')
def index(request):
    return HTTPFound(request.static_path('imaginationwebui:static/'))


@view_config(route_name='list', renderer='json')
def list(request):
    return request.registry.slides.get()


@view_config(route_name='reorder', renderer='json')
def reorder(request):
    slides = request.registry.slides.get()
    for position, slide in enumerate(request.params.get('order').split('|')):
        slides[slide]['position'] = position
    request.registry.slides.set(slides)
    return slides


@view_config(route_name='update', renderer='string')
def update(request):
    slides = request.registry.slides.get()
    slides[request.params['slide']]['text'] = request.params.get('text', '')
    request.registry.slides.set(slides)
    return 'update successful'


@view_config(route_name='export', renderer='config.img.mak')
def export(request):
    request.response.content_type = 'text/plain'
    slides = request.registry.slides.get()
    return {'slides': slides.values()}


@view_config(route_name='flickrimport', renderer='json')
def flickrimport(request):
    setid = request.params.get('setid', '72157633137000735')
    slides = {} if asbool(request.params.get('erase', False)) \
                else request.registry.slides.get()

    # urltype > (suffix from http://www.flickr.com/services/api/misc.urls.html)
    thumb_urltypes = [
            'url_n',  # (suffix n) small, 320 on longest side
            'url_s',  # (suffix m) small, 240 on longest side
            'url_t',  # (suffix t) thumbnail, 100 on longest side
           #'url_sq', # (suffix s) small square 75x75
            ]
    urltypes = [
            'url_o',  # (suffix o) original image
            'url_l',  # (suffix b) large, 1024 on longest side
            'url_c',  # (suffix c) medium 800, 800 on longest side
            'url_z',  # (suffix z) medium 640, 640 on longest side
            'url_m',  # (suffix -) medium, 500 on longest side
            ] + thumb_urltypes

    url = 'http://api.flickr.com/services/rest/' \
            '?method=flickr.photosets.getPhotos' \
            '&api_key=70df7978819efb94c7efb85a2f3313e7' \
            '&photoset_id=%s&format=json&nojsoncallback=1' \
            '&extras=%s' % (setid, ','.join(urltypes))
    data = json.load(urllib2.urlopen(url))

    photos = data['photoset']['photo']
    thumb_urls = map(itemgetter('thumb_url'), slides.values())
    count = len(slides)

    def _find_urls(photo):
        """This will return the urls (thumb_url, url) for the biggest photo
        available or None if the photo already exists in the datastore"""
        thumb_url = None
        url = None
        for t in thumb_urltypes:
            if t in photo:
                if photo[t] in thumb_urls:
                    return None, None
                thumb_url = photo[t]
                break
        for t in urltypes:
            if t in photo:
                url = photo[t]
                break
        return thumb_url, url

    for photo in photos:
        thumb_url, url = _find_urls(photo)
        if thumb_url is None:
            continue

        slides[str(count)] = {
                'thumb_url': thumb_url,
                'url': url,
                'text': photo['title'],
                'position': count,
                }
        count += 1
    request.registry.slides.set(slides)
    return slides
