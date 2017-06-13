"""Database models to work within the briefy.leica system."""
from briefy.common.db.models.roles import LocalRoleDeprecated
from briefy.leica.db import Session
from briefy.leica.models.asset import Asset
from briefy.leica.models.asset import Image
from briefy.leica.models.asset import ThreeSixtyImage
from briefy.leica.models.asset import Video
from briefy.leica.models.billing_info.customer import CustomerBillingInfo
from briefy.leica.models.billing_info.professional import ProfessionalBillingInfo
from briefy.leica.models.comment import Comment
from briefy.leica.models.customer import Customer
from briefy.leica.models.customer.address import CustomerBillingAddress
from briefy.leica.models.customer.contact import CustomerContact
from briefy.leica.models.job import Assignment
from briefy.leica.models.job import IAssignment  # noQA
from briefy.leica.models.job.leadorder import LeadOrder
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
from briefy.leica.models.user import BriefyUserProfile
from briefy.leica.models.user import CustomerUserProfile
from briefy.leica.models.user import UserProfile
from briefy.ws.listeners import register_workflow_context_listeners

import sqlalchemy as sa


LocalRoleDeprecated.__session__ = Session

ALL_MODELS = [
    AdditionalWorkingLocation,
    Asset,
    Assignment,
    BriefyUserProfile,
    Comment,
    Customer,
    CustomerUserProfile,
    CustomerBillingAddress,
    CustomerBillingInfo,
    CustomerContact,
    Image,
    Facebook,
    FiveHundred,
    Flickr,
    GDrive,
    Instagram,
    LeadOrder,
    Link,
    Linkedin,
    LocalRoleDeprecated,
    MainWorkingLocation,
    Order,
    OrderLocation,
    Photographer,
    Pool,
    Professional,
    ProfessionalBillingInfo,
    ProfessionalsInPool,
    Project,
    Portfolio,
    ThreeSixtyImage,
    Tumblr,
    Twitter,
    UserProfile,
    Video,
    Videographer,
    Youtube,
]

# register sqlalchemy workflow context event handlers
register_workflow_context_listeners(ALL_MODELS)

sa.orm.configure_mappers()
