"""Briefy Leica."""
from briefy import leica
from briefy.common.db.model import Base
from briefy.leica.db import get_db
from briefy.leica.db import get_engine
from briefy.leica.db import Session
from pyramid.config import Configurator
from zope.configuration.xmlconfig import XMLConfig


import briefy.ws
import logging
import pkg_resources

__version__ = pkg_resources.get_distribution(__package__).version
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
cs = logging.StreamHandler()
cs.setLevel(logging.INFO)
logger.addHandler(cs)

XMLConfig('configure.zcml', leica)()


def main(global_config, debug=False, **settings):
    """Return a Pyramid WSGI application."""
    settings = briefy.ws.expandvars_dict(settings)
    engine = get_engine(settings)
    settings['config_file'] = (
        getattr(global_config, '__file__', None) or global_config.get('__file__', '')
    )
    Session.configure(bind=engine)
    Base.metadata.bind = engine
    config = Configurator(
        settings=settings
    )
    config.registry['debug'] = debug
    config.registry['db_session_factory'] = Session
    config.add_request_method(get_db, 'db', reify=True)
    config.include('briefy.ws')
    briefy.ws.initialize(config, version=__version__, project_name=__name__)
    config.scan()
    return config.make_wsgi_app()
