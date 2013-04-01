import io
import transaction
import ConfigParser

from pyramid.config import Configurator
from pyramid.events import NewRequest
from pyramid.events import subscriber
from acidfs import AcidFS


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)

    afs = AcidFS(settings['acidfs.repository'])
    config.registry.afs = afs
    config.registry.slides = get_slides(afs, settings)

    config.include('pyramid_tm')
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('list', '/')
    config.add_route('update', '/update')
    config.add_route('reorder', '/reorder')
    config.add_route('export', '/export')
    config.scan()
    return config.make_wsgi_app()


def get_slides(afs, settings):
    imgdefault = settings['imagination_default']
    imgpath = settings['acidfs.imaginationpath']
    if afs.exists(imgpath):
        with afs.open(imgpath, 'r') as f:
            imgtext = f.read()
    else:
        with open(imgdefault, 'r') as f:
            imgtext = f.read()
    imgconfig = ConfigParser.RawConfigParser(allow_no_value=True)
    imgconfig.readfp(io.BytesIO(imgtext))
    slides = {}
    for i in range(imgconfig.getint('slideshow settings', 'number of slides')):
        slide = 'slide %d' % (i + 1)
        url = imgconfig.get(slide, 'filename')
        slides[str(i)] = {
                'url': url,
                'text': imgconfig.get(slide, 'text'),
                'position': i
                }
    return slides


@subscriber(NewRequest)
def set_user(event):
    transaction.get().setUser("Anonymous")
