import json
import hashlib
import urllib2
from operator import itemgetter

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound, HTTPConflict, HTTPForbidden
from pyramid.settings import asbool
from pyramid.security import (authenticated_userid, remember, forget)
from flickrapi import FlickrAPI
from flickrapi.exceptions import FlickrError


def get_flickr_from_session(request):
    f = FlickrAPI(
            request.registry.settings['flickr.key'],
            request.registry.settings['flickr.secret'],
            token=None,
            store_token=False)
    session = request.session
    if 'request_token' in session:
        f.flickr_oauth.resource_owner_key = session['request_token']
        f.flickr_oauth.resource_owner_secret = session['request_token_secret']
        f.flickr_oauth.requested_permissions = session['requested_permissions']
    elif authenticated_userid(request):
        # an authenticated user should have the request_token in session
        raise HTTPForbidden()
    return f


def set_session_from_flickr(request, flickr):
    session = request.session
    session['request_token'] = flickr.flickr_oauth.resource_owner_key
    session['request_token_secret'] = flickr.flickr_oauth.resource_owner_secret
    session['requested_permissions'] = \
        flickr.flickr_oauth.requested_permissions or u'read'


@view_config(context=HTTPForbidden)
@view_config(route_name='flickr_login')
def flickr_login(request):
    f = get_flickr_from_session(request)
    # Do not allow a user to login if they are already logged in
    # if authenticated_userid(request) and f.token_valid(perms=u'read'):
    #     return HTTPForbidden()
    if authenticated_userid(request):
      try:
          resp = f.auth.oauth.checkToken(format='etree')
          token_perms = resp.findtext('oauth/perms')
          if token_perms == f.flickr_oauth.requested_permissions:
              return HTTPForbidden()
      except FlickrError:
          pass

    f.get_request_token(oauth_callback=request.route_url('flickr_callback'))
    set_session_from_flickr(request, f)
    return HTTPFound(location=f.auth_url(perms='read'))


@view_config(route_name='flickr_callback', request_method='GET')
def flickr_callback(request):
    f = get_flickr_from_session(request)
    f.get_access_token(request.params.get('oauth_verifier'))
    set_session_from_flickr(request, f)
    headers = remember(request, f.flickr_oauth.token.user_nsid)
    return HTTPFound(
            location=request.route_url('flickr_import'), headers=headers)


@view_config(route_name='flickr_logout')
def flickr_logout(request):
    headers = forget(request)
    session = request.session
    if 'request_token' in session:
        del session['request_token']
        del session['request_token_secret']
        del session['requested_permissions']
    return HTTPFound(
            location=request.route_url('flickr_import'), headers=headers)


@view_config(route_name='flickr_import', request_method='GET',
    renderer='templates/flickr_import.html.mak')
def flickr_import(request):
    return {
        "flickr": get_flickr_from_session(request)
        }


@view_config(route_name='flickr_import_setid')
def flickr_import_setid(request):
    set_id = request.matchdict['set_id']
    f = get_flickr_from_session(request)

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

    data = f.photosets.getPhotos(
        user_id=request.authenticated_userid,
        photoset_id=set_id,
        extras=','.join(urltypes),
        format='parsed-json')
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
    return HTTPFound(request.route_url('index'))


@view_config(route_name='index')
def index(request):
    return HTTPFound(request.static_path('imaginationwebui:static/'))


@view_config(route_name='list', renderer='json', http_cache=0)
def list(request):
    maxsize = int(request.params.get('size', 3))
    slides = request.registry.slides.get()
    for slide in slides.itervalues():
        thumb_urls = slide['thumb_urls']
        del slide['thumb_urls']
        size = min(maxsize, len(thumb_urls) - 1)
        slide['thumb_url'] = thumb_urls[-(size + 1)]
    return slides


def get_remote_md5_sum(url, max_file_size=100*1024*1024):
    remote = urllib2.urlopen(url)
    hash = hashlib.md5()
    total_read = 0
    while True:
        data = remote.read(4096)
        total_read += 4096
        if not data or total_read > max_file_size:
            break
        hash.update(data)
    return hash.hexdigest()


@view_config(route_name='listbymd5', renderer='json')
def listbymd5(request):
    slides = request.registry.slides.get()
    bymd5 = {}
    for key, slide in slides.iteritems():
        slide['id'] = key
        bymd5[get_remote_md5_sum(slide['thumb_urls'][-1])] = slide
    return bymd5


@view_config(route_name='orderedlist', renderer='json')
def orderedlist(request):
    slides = request.registry.slides.get()
    orderedslides = []
    for key, slide in slides.iteritems():
        slide['id'] = key
        orderedslides.append(slide)
    orderedslides.sort(key=itemgetter('position'))
    return orderedslides


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
    if slide['text'] == text:
        return 'nothing to update'
    if request.params.get('initial_text') != slide['text']:
        return HTTPConflict()
    slide['text'] = text
    request.registry.slides.set(slides)
    return 'update successful'


@view_config(route_name='export', renderer='config.img.mak')
def export(request):
    request.response.content_type = 'text/plain'
    slides = request.registry.slides.get().values()
    slides.sort(key=itemgetter('position'))
    until = request.params.get('until')
    if until:
        del slides[next((i for i, v in enumerate(slides)
            if until in v['text']), len(slides)):]
    return {'slides': slides}
