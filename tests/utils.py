"""Utils to export db data to json."""
from briefy.leica.models import Asset
from briefy.leica.models import Assignment
from briefy.leica.models import Comment
from briefy.leica.models import Customer
from briefy.leica.models import Project


DATA_PATH = 'data/'


def export_model(file_name, model):
    """Export one entity to json"""
    file_name = DATA_PATH + file_name
    file = open(file_name, 'w')
    file.write('[')
    for item in model.query().all():
        file.write('{0},'.format(item.to_JSON()))
    file.write(']')
    file.flush()


def export_all():
    """Export all data to json files."""
    export_model('assets.json', Asset)
    export_model('comments.json', Comment)
    export_model('customers.json', Customer)
    export_model('assignments.json', Assignment)
    export_model('projects.json', Project)
