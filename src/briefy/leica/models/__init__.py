""" Database models to work within the briefy.leica system """
from .asset import Asset
from .comment import Comment
from .comment import InternalComment
from .customer import Customer
from .job import Job
from .job import IJob  # noQA
from .job_location import JobLocation
from .professional import Professional
from .project import Project


ALL_MODELS = [Asset, Comment, Customer, InternalComment, Job, JobLocation, Professional, Project]
