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
    return request.registry.slides


@view_config(route_name='reorder', renderer='json')
def reorder(request):
    for position, slide in enumerate(request.params.get('order').split('|')):
        request.registry.slides[slide]['position'] = position
    return request.registry.slides


@view_config(route_name='update', renderer='string')
def update(request):
    request.registry.slides[request.params['slide']]['text'] = \
            request.params.get('text', '')
    return 'update successful'


@view_config(route_name='export', renderer='config.img.mak')
def export(request):
    request.response.content_type = 'text/plain'
    return {'slides': request.registry.slides.values()}


@view_config(route_name='flickrimport', renderer='json')
def flickrimport(request):
    setid = request.params.get('setid', '72157633137000735')
    slides = {} if asbool(request.params.get('erase', False)) \
                else request.registry.slides
    url = 'http://api.flickr.com/services/rest/' \
            '?method=flickr.photosets.getPhotos' \
            '&api_key=268c0d669b7b50a951bd0d6bb9ab2669' \
            '&photoset_id=%s&format=json&nojsoncallback=1' \
            '&extras=url_n,url_o,url_l' % setid
            #'&api_key=2a2ce06c15780ebeb0b706650fc890b2'
    data = json.load(urllib2.urlopen(url))
    photos = data['photoset']['photo']
    urls = map(itemgetter('url'), slides.values())
    count = len(slides)
    for photo in photos:
        if photo['url_n'] in urls:
            continue
        slides[str(count)] = {
                'url': photo['url_n'],
                'text': photo['title'],
                'position': count,
                }
        count += 1
    request.registry.slides = slides
    return slides
