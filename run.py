""" Toy server to play around during development """

import briefy.leica
import briefy.leica.config as conf
from wsgiref.simple_server import make_server

app = briefy.leica.main(conf, sqlalchemy_url='sqlite://')
server = make_server('', 8000, app)
server.serve_forever()
