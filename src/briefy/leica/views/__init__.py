from .assets import get_asset

"""View to handle Leads creation."""

from briefy.leica.config import FILE_PICKER_API_KEY
from briefy.leica.models import Asset
from briefy.ws import CORS_POLICY
from cornice import Service
from sqlalchemy import event
from sqlalchemy import func as sa_func

import transaction

leica = Service(
    name='Leica',
    path='/images',
    cors_policy=CORS_POLICY
)




file_picker_js = """
<script type="text/javascript" src="//api.filestackapi.com/filestack.js"></script>

<input type="filepicker" data-fp-apikey="" data-fp-mimetypes="image/*" data-fp-container="modal" data-fp-multiple="true" data-fp-services="CLOUDDRIVE,COMPUTER,DROPBOX,GOOGLE_DRIVE,FLICKR,GMAIL,INSTAGRAM,SKYDRIVE,URL,PICASA,FTP" onchange="out='';for(var i=0;i<event.fpfiles.length;i++){{out+=event.fpfiles[i].url;out+=' '}};alert(out)">
""".format(key=FILE_PICKER_API_KEY)


@leica.get()
def root(request):
    return {'key': FILE_PICKER_API_KEY}


@leica.post()
def get_urls(request):
    return {'status': 'ok'}


#leica = Service(
    #name='Demo',
    #path='/demo',
    #cors_policy=CORS_POLICY
#)

from pyramid.view import view_config
@view_config(physical_path='/hello')
def hello(request):
    return("<h1>World</h1>")

