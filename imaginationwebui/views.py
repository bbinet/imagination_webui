from pyramid.view import view_config
from pyramid.response import Response


@view_config(route_name='list', renderer='json')
def list(request):
    slides = []
    imgconfig = request.registry.imgconfig
    nb_slides = imgconfig.getint('slideshow settings', 'number of slides')
    for i in range(nb_slides):
        slide = 'slide %d' % (i + 1)
        slides.append({
            'url': imgconfig.get(slide, 'filename'),
            'text': imgconfig.get(slide, 'text'),
            })
    return slides


@view_config(route_name='update', renderer='string')
def update(request):
    return 'update'


@view_config(route_name='export')
def export(request):
    resp = Response(content_type='text/plain')
    request.registry.imgconfig.write(resp.body_file)
    return resp
