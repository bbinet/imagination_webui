import json
import urllib2
from operator import itemgetter

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound, HTTPConflict
from pyramid.settings import asbool


@view_config(route_name='index')
def index(request):
    return HTTPFound(request.static_path('imaginationwebui:static/'))


@view_config(route_name='list', renderer='json')
def list(request):
    maxsize = int(request.params.get('size', 3))
    slides = request.registry.slides.get()
    for slide in slides.itervalues():
        thumb_urls = slide['thumb_urls']
        del slide['thumb_urls']
        size = min(maxsize, len(thumb_urls) - 1)
        slide['thumb_url'] = thumb_urls[-(size + 1)]
    return slides


@view_config(route_name='reorder', renderer='json')
def reorder(request):
    slides = request.registry.slides.get()
    order = [k for k, v in sorted(
        slides.iteritems(), key=lambda x: x[1]['position'])]
    if request.params.get('initial_order') != '|'.join(order):
        return HTTPConflict()
    for position, slide in enumerate(request.params.get('order').split('|')):
        slides[slide]['position'] = position
    request.registry.slides.set(slides)
    return slides


@view_config(route_name='update', renderer='string')
def update(request):
    text = request.params.get('text', '')
    slides = request.registry.slides.get()
    slide = slides[request.params['slide']]
    if request.params.get('initial_text') != slide['text']:
        return HTTPConflict()
    if slide['text'] == text:
        return 'nothing to update'
    slide['text'] = text
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
            'url_m',  # (suffix -) medium, 500 on longest side
            'url_n',  # (suffix n) small, 320 on longest side
            'url_s',  # (suffix m) small, 240 on longest side
            'url_t',  # (suffix t) thumbnail, 100 on longest side
            'url_sq',  # (suffix s) small square 75x75
            ]
    urltypes = [
            'url_o',  # (suffix o) original image
            'url_l',  # (suffix b) large, 1024 on longest side
            'url_c',  # (suffix c) medium 800, 800 on longest side
            'url_z',  # (suffix z) medium 640, 640 on longest side
            ] + thumb_urltypes

    url = 'http://api.flickr.com/services/rest/' \
            '?method=flickr.photosets.getPhotos' \
            '&api_key=2a2ce06c15780ebeb0b706650fc890b2' \
            '&photoset_id=%s&format=json&nojsoncallback=1' \
            '&extras=%s' % (setid, ','.join(urltypes))
    data = json.load(urllib2.urlopen(url))

    photos = data['photoset']['photo']
    urls = map(itemgetter('url'), slides.values())
    count = len(slides)

    def _find_urls(photo):
        """This will return the urls (thumb_urls, url) for the biggest photo
        available or None if the photo already exists in the datastore"""
        url = None
        for t in urltypes:
            if t in photo:
                if photo[t] in urls:
                    return None, None
                url = photo[t]
                break
        thumb_urls = []
        for t in thumb_urltypes:
            if t in photo:
                thumb_urls.append(photo[t])
        return thumb_urls, url

    for photo in photos:
        thumb_urls, url = _find_urls(photo)
        if url is None:
            continue
        slides[str(count)] = {
                'thumb_urls': thumb_urls,
                'url': url,
                'text': photo['title'],
                'position': count,
                }
        count += 1
    request.registry.slides.set(slides)
    return slides
