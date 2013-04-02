import json

from pyramid.config import Configurator
from pyramid.events import NewRequest
from pyramid.events import subscriber
from acidfs import AcidFS
import transaction


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)

    afs = AcidFS(settings['acidfs.repository'])
    config.registry.afs = afs
    config.registry.slides = get_slides(afs, settings)

    config.include('pyramid_tm')
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('index', '/')
    config.add_route('list', '/list')
    config.add_route('update', '/update')
    config.add_route('reorder', '/reorder')
    config.add_route('export', '/export')
    config.add_route('flickrimport', '/flickrimport')
    config.scan()
    return config.make_wsgi_app()


def get_slides(afs, settings):
    imgpath = settings['acidfs.imaginationpath']
    slides = {}
    if afs.exists(imgpath):
        with afs.open(imgpath, 'r') as f:
            slides = json.load(f)
    return slides


@subscriber(NewRequest)
def set_user(event):
    transaction.get().setUser("Anonymous")
