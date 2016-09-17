"""Utils to export db data to json."""
from briefy.leica.models import Asset
from briefy.leica.models import Comment
from briefy.leica.models import Job
from briefy.leica.models import Project


DATA_PATH = 'data/'


def export_model(file_name, model):
    """Export one entity to json"""
    file_name = DATA_PATH + file_name
    file = open(file_name, 'w')
    file.write('[')
    for item in model.query().all():
        file.write('{},'.format(item.to_JSON()))
    file.write(']')
    file.flush()


def export_all():
    """Export all data to json files."""
    export_model('assets.json', Asset)
    export_model('comments.json', Comment)
    export_model('jobs.json', Job)
    export_model('projects.json', Project)
