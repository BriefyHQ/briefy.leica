from briefy.leica.models import IJob

from zope.component import adapter
from zope.interface import Interface
from zope.interface import implementer

KNACK_KEY = '_knack'


class IKnackObject(Interface):
    """Marker interface for objects comming from Knack database"""


@adapter(IKnackObject)
@implementer(IJob)
class KnackJob:

    def __init__(self, knack_job):
        self.knack_job = knack_job
