"""Database models to work within the briefy.leica system."""
import sqlalchemy as sa
from briefy.common.db.models.roles import LocalRole
from briefy.ws.listeners import register_workflow_context_listeners

from briefy.leica.db import Session
from briefy.leica.models.asset import Asset
from briefy.leica.models.asset import Image
from briefy.leica.models.asset import ThreeSixtyImage
from briefy.leica.models.asset import Video
from briefy.leica.models.comment import Comment
from briefy.leica.models.customer import Customer
from briefy.leica.models.customer.address import CustomerBillingAddress
from briefy.leica.models.customer.contact import CustomerContact
from briefy.leica.models.job import Assignment
from briefy.leica.models.job import IAssignment  # noQA
from briefy.leica.models.job.location import OrderLocation
from briefy.leica.models.job.order import Order
from briefy.leica.models.job.pool import Pool
from briefy.leica.models.job.pool import ProfessionalsInPool
from briefy.leica.models.professional import Photographer
from briefy.leica.models.professional import Professional
from briefy.leica.models.professional import Videographer
from briefy.leica.models.professional.link import Facebook
from briefy.leica.models.professional.link import FiveHundred
from briefy.leica.models.professional.link import Flickr
from briefy.leica.models.professional.link import GDrive
from briefy.leica.models.professional.link import Instagram
from briefy.leica.models.professional.link import Link  # noQA
from briefy.leica.models.professional.link import Linkedin
from briefy.leica.models.professional.link import Portfolio
from briefy.leica.models.professional.link import Tumblr
from briefy.leica.models.professional.link import Twitter
from briefy.leica.models.professional.link import Youtube
from briefy.leica.models.professional.location import AdditionalWorkingLocation
from briefy.leica.models.professional.location import MainWorkingLocation
from briefy.leica.models.professional.location import WorkingLocation  # noQA
from briefy.leica.models.project import Project

LocalRole.__session__ = Session

ALL_MODELS = [
    AdditionalWorkingLocation,
    Asset,
    Assignment,
    Comment,
    Customer,
    CustomerBillingAddress,
    CustomerContact,
    Image,
    Facebook,
    FiveHundred,
    Flickr,
    GDrive,
    Instagram,
    Link,
    Linkedin,
    LocalRole,
    MainWorkingLocation,
    Order,
    OrderLocation,
    Photographer,
    Pool,
    Professional,
    ProfessionalsInPool,
    Project,
    Portfolio,
    ThreeSixtyImage,
    Tumblr,
    Twitter,
    Video,
    Videographer,
    Youtube,
]

# register sqlalchemy workflow context event handlers
register_workflow_context_listeners(ALL_MODELS)

sa.orm.configure_mappers()
