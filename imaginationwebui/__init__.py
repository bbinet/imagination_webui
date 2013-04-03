from pyramid.config import Configurator
from pyramid.events import NewRequest
from pyramid.events import subscriber
import transaction

from .lib import SlidesDataStore


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)

    config.registry.slides = SlidesDataStore(settings['acidfs.repository'])

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


@subscriber(NewRequest)
def set_user(event):
    transaction.get().setUser("ImaginationWebUI")
