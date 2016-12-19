"""Database models to work within the briefy.leica system."""
from briefy.common.db.models.roles import LocalRole
from briefy.leica.db import Session
from briefy.leica.models.asset import Asset
from briefy.leica.models.asset import Image
from briefy.leica.models.asset import ThreeSixtyImage
from briefy.leica.models.asset import Video
from briefy.leica.models.comment import Comment
from briefy.leica.models.customer import Customer
from briefy.leica.models.customer.address import CustomerBillingAddress
from briefy.leica.models.customer.contact import CustomerContact
from briefy.leica.models.job import IJob  # noQA
from briefy.leica.models.job import JobAssignment
from briefy.leica.models.job.order import JobOrder
from briefy.leica.models.job.location import JobLocation
from briefy.leica.models.professional import Photographer
from briefy.leica.models.professional import Professional
from briefy.leica.models.professional import Videographer
from briefy.leica.models.professional.link import Facebook
from briefy.leica.models.professional.link import Flickr
from briefy.leica.models.professional.link import Instagram
from briefy.leica.models.professional.link import Link  # noQA
from briefy.leica.models.professional.link import Portfolio
from briefy.leica.models.professional.link import Tumblr
from briefy.leica.models.professional.link import Twitter
from briefy.leica.models.professional.link import Youtube
from briefy.leica.models.professional.location import AdditionalWorkingLocation
from briefy.leica.models.professional.location import MainWorkingLocation
from briefy.leica.models.professional.location import WorkingLocation  # noQA
from briefy.leica.models.project import Project
from briefy.ws.listeners import register_workflow_context_listeners

import sqlalchemy as sa

LocalRole.__session__ = Session

ALL_MODELS = [
    AdditionalWorkingLocation,
    Asset,
    Image,
    ThreeSixtyImage,
    Video,
    Comment,
    Customer,
    CustomerBillingAddress,
    CustomerContact,
    Facebook,
    Flickr,
    Instagram,
    JobAssignment,
    JobLocation,
    JobOrder,
    Link,
    LocalRole,
    MainWorkingLocation,
    Photographer,
    Portfolio,
    Professional,
    Project,
    Tumblr,
    Twitter,
    Videographer,
    Youtube,
]


# register sqlalchemy workflow context event handlers
register_workflow_context_listeners(ALL_MODELS)

sa.orm.configure_mappers()
