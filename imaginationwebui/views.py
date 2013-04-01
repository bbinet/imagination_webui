from pyramid.view import view_config
from pyramid.response import Response


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
    return 'update'


@view_config(route_name='export', renderer='config.img.mak')
def export(request):
    request.response.content_type = 'text/plain'
    return {'slides': request.registry.slides.values()}
