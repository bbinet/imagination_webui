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
    config.registry.imgconfig = get_imgconfig(afs, settings)

    config.include('pyramid_tm')
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('list', '/')
    config.add_route('show', '/')
    config.add_route('update', '/update')
    config.scan()
    return config.make_wsgi_app()


def get_imgconfig(afs, settings):
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
    return imgconfig


@subscriber(NewRequest)
def set_user(event):
    transaction.get().setUser("Anonymous")
