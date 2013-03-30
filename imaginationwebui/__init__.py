import transaction

from pyramid.config import Configurator
from pyramid.events import NewRequest
from pyramid.events import subscriber
from acidfs import AcidFS


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)

    config.registry.afs = AcidFS(settings['acidfs.repository'])

    config.include('pyramid_tm')
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('show', '/')
    config.add_route('update', '/update')
    config.scan()
    return config.make_wsgi_app()


@subscriber(NewRequest)
def set_user(event):
    transaction.get().setUser("Anonymous")
