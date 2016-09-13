"""Views to handle Asset handling creation."""

from briefy.leica.models import Asset
# from briefy.leica.validators import AssetSchema
from briefy.ws import CORS_POLICY
from cornice import Service
# from sqlalchemy import event
# from sqlalchemy import func as sa_func

import transaction

asset = Service(
    name='asset',
    path='/asset/{id:.*}',
    cors_policy=CORS_POLICY
)



@asset.get()
def get_asset(request):
    """Get content an information about an asset"""
    id = request.matchdict.get('id', '')
    #import pdb; pdb.set_trace()

    return {
        'author': id,
        'url': '',
        'comments': ['hello', 'world']
    }


