from pyramid.config import Configurator
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.events import NewRequest
from pyramid.events import subscriber
from pyramid.session import SignedCookieSessionFactory
import transaction

from .lib import SlidesDataStore


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """

    authn_policy = AuthTktAuthenticationPolicy(settings['auth.secret'])
    session_factory = SignedCookieSessionFactory(settings['session.secret'])
    config = Configurator(
            settings=settings,
            authentication_policy=authn_policy,
            session_factory=session_factory)

    config.registry.slides = SlidesDataStore(settings['acidfs.repository'])

    config.include('pyramid_tm')
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('index', '/')
    config.add_route('list', '/list')
    config.add_route('orderedlist', '/orderedlist')
    config.add_route('listbymd5', '/listbymd5')
    config.add_route('update', '/update')
    config.add_route('reorder', '/reorder')
    config.add_route('export', '/export')
    config.add_route('flickr_import', '/flickr/import')
    config.add_route('flickr_import_setid', '/flickr/import/{set_id:\d+}')
    config.add_route('flickr_callback', '/flickr/callback')
    config.add_route('flickr_login', '/flickr/login')
    config.add_route('flickr_logout', '/flickr/logout')
    config.scan()
    return config.make_wsgi_app()


@subscriber(NewRequest)
def set_user(event):
    transaction.get().setUser("ImaginationWebUI")
