""" Database models to work within the briefy.leica system """
from .asset import Asset
from .job import IJob
from .job import Job
from .job import JobLocation
from .project import Project
from .project import IProject
from .asset import Asset



ALL_MODELS = [Asset, Job, JobLocation, Project]
