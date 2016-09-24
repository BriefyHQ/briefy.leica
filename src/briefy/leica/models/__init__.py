"""Database models to work within the briefy.leica system."""
from .asset import Asset
from .comment import Comment
from .comment import InternalComment
from .customer import Customer
from .job import Job
from .job import IJob  # noQA
from .job_location import JobLocation
from .professional import Professional
from .project import Project
from briefy.ws.listeners import register_workflow_context_listeners

import sqlalchemy as sa


ALL_MODELS = [Asset, Comment, Customer, InternalComment, Job, JobLocation, Professional, Project]

# register sqlalchemy workflow context event handlers
register_workflow_context_listeners(ALL_MODELS)


sa.orm.configure_mappers()
