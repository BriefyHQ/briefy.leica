"""Add pool_id and delivery config to projects.

Revision ID: 60bc86209022
Revises: c1674bf2a6bb
Create Date: 2017-02-17 17:20:15.497013
"""
from alembic import op
from sqlalchemy_utils import types

import json
import sqlalchemy as sa

revision = '60bc86209022'
down_revision = 'c1674bf2a6bb'
branch_labels = None
depends_on = None

PROJECT_DELIVERY_CONFIG = {
    '648cb92d-6f14-4d7b-98e6-d0f7c65a99b9': {
        'archive': '0B2QYuPa8WdDseW11UkwyOWlpUzg', 'delivery': '0B2QYuPa8WdDsSXU5RHRXMHZvcVU'
    },
    'daae8dc3-b8b8-49b4-8c09-6e5dd64c29de': {
        'archive': '0B2QYuPa8WdDseW11UkwyOWlpUzg', 'delivery': '0B2QYuPa8WdDsSXU5RHRXMHZvcVU'
    },
    '18f2d83f-b124-4825-a967-43fb031868ed': {
        'archive': '0B2QYuPa8WdDseW11UkwyOWlpUzg', 'delivery': '0B2QYuPa8WdDsSXU5RHRXMHZvcVU'
    },
    '674e1d10-4989-4600-b082-acd30dc0d5a4': {
        'archive': '0B2QYuPa8WdDseW11UkwyOWlpUzg', 'delivery': '0B2QYuPa8WdDsSXU5RHRXMHZvcVU'
    },
    '0f3accec-946c-43d7-8935-44223cbd3553': {
        'archive': '0BwrdIL719n7wSnVKX05iOUlCdlU', 'delivery': '0BwrdIL719n7wVURQUC1VS2VKY0E'
    },
    '4e7976d5-1a7f-4cfa-b6ba-08356bc7f162': {
        'archive': '0BwrdIL719n7wSnVKX05iOUlCdlU', 'delivery': '0BwrdIL719n7wVURQUC1VS2VKY0E'
    },
    '6bc29461-8a6e-4d10-bd54-f48d498f7776': {
        'archive': '0BwrdIL719n7wSnVKX05iOUlCdlU', 'delivery': '0BwrdIL719n7wVURQUC1VS2VKY0E'
    },
    '2edf1e7b-b7f0-4ca4-8d1b-9a8baf05662c': {
        'archive': '0BwrdIL719n7wSnVKX05iOUlCdlU', 'delivery': '0BwrdIL719n7wVURQUC1VS2VKY0E'
    },
    '1dafb433-9431-4295-a349-92c4ad61c59e': {
        'archive': '0BwrdIL719n7wSnVKX05iOUlCdlU', 'delivery': '0BwrdIL719n7wVURQUC1VS2VKY0E'
    },
    'd1f38481-597a-4223-b059-37f13603eb09': {
        'archive': '0BwrdIL719n7wajZqMkp6TVFNRjA', 'delivery': '0BwrdIL719n7wV2h5MVFBNnViaWc'
    },
    'ff9e8a4b-27ae-474f-94b5-148316ebd0c9': {
        'archive': '0BwrdIL719n7wb3U2cm9uZENmRFU', 'delivery': '0BwrdIL719n7wU3U2dkZGdFVvRkE'
    },
    '49f8b115-00f2-415e-a417-c4ecd5395be6': {
        'archive': '0B2QYuPa8WdDsY01uYl9ESVhsMkE', 'delivery': '0B2QYuPa8WdDsWU5sT3d6TGNqOW8'
    },
    '6875b534-67ac-469d-979a-e5d7f4d147e5': {
        'archive': '0B2QYuPa8WdDsX2JQUlpNamRmcVU', 'delivery': '0B2QYuPa8WdDsdVdDYXZiUTdyUUE'
    },
    'd53f54fe-580e-4ab1-8f0e-abda90eff210': {
        'archive': '0BwrdIL719n7wZmZuMzNWbFRWbjg', 'delivery': '0BwrdIL719n7wZWtCLTZ0Mk5oMWM'
    },
    '1c44a368-ee9b-4289-ae20-6a28c28149c0': {
        'archive': '0BwrdIL719n7waGRibl90Y0luU2c', 'delivery': '0BwrdIL719n7wMC1CN25QUnZndWc'
    },
    '92c4cf14-f4bf-4747-9661-3008d4210ad3': {
        'archive': '0BwrdIL719n7wRDVCUzIyMjdJb28', 'delivery': '0BwrdIL719n7wYndhRzZBUTQ4ZXM'
    },
    'ac219357-0273-4e54-ab57-470cbf2467e3': {
        'archive': '0B2QYuPa8WdDsY2Y0WjN5M1NTaTQ', 'delivery': '0B1Cpa54F2k6vOWdLXzZqenZhSXM'
    },
    '7348609b-23a3-43b2-a9c6-9db698c25cf7': {
        'archive': '0BwrdIL719n7wZUhyaXdvek85bzA', 'delivery': '0BwrdIL719n7wQ1pxN2xlWDB0SHc'
    },
    '93e0dc8f-1d12-4821-884c-72040c7e2e82': {
        'archive': '0BwrdIL719n7waVRIVjRhQ0FtSVk', 'delivery': '0BwrdIL719n7wQUc5ZW9hNXBfU1k'
    },
    '445f0569-ddf5-4b18-860a-ff29db3d220a': {
        'archive': '0BwrdIL719n7wTXN3VGNycktPenc', 'delivery': '0BwrdIL719n7wMERDZExxREwyQ28'
    },
    '532c6775-3431-4af4-8448-6978e8d76185': {
        'archive': '0BwrdIL719n7wVkVERC1pYkNCZk0', 'delivery': '0BwrdIL719n7wSmUwLWhSM0p1bUU'
    },
    'a130b920-6269-4f5e-ae1d-b73e0fce95ff': {
        'archive': '0B2QYuPa8WdDsdld6aktydV9JU2c', 'delivery': '0B2QYuPa8WdDsaHVJeWdIdWdZYjg'
    },
    '1df6f838-1fcb-48ac-9034-40126f469a18': {
        'archive': '0BwrdIL719n7wVks2RmtwRjdIUkU', 'delivery': '0BwrdIL719n7wWTRzVWRKdFV2TXc'
    },
    'd347be4c-eddc-4d9d-9fd8-4bbd24d3e13b': {
        'archive': '0BwrdIL719n7wYWxNN0F4QnBXbHc', 'delivery': '0BwrdIL719n7wMkpXMmhfWDY4bkU'
    },
}

UPDATES = """
UPDATE PROJECTS SET pool_id='009e2b7c-cc61-4f7b-ac34-7ced9a6bc0f5' WHERE id='1dafb433-9431-4295-a349-92c4ad61c59e';
UPDATE PROJECTS SET pool_id='83b1f333-b270-43fd-8922-234bbdfaa855' WHERE id='2edf1e7b-b7f0-4ca4-8d1b-9a8baf05662c';
UPDATE PROJECTS SET pool_id='9d416e3f-39ce-4419-bb0a-d4d882f1fbf2' WHERE id='6bc29461-8a6e-4d10-bd54-f48d498f7776';
UPDATE PROJECTS SET pool_id='cddc09d1-cd92-4fde-be42-11e3cdd34e19' WHERE id='4e7976d5-1a7f-4cfa-b6ba-08356bc7f162';
UPDATE PROJECTS SET pool_id='04b71171-f032-452a-b31f-2ba179b2c360' WHERE id='78246086-ae6d-424c-b77e-aa7a8cb81035';
UPDATE PROJECTS SET pool_id='92032655-8c85-4480-a241-b3eb68d7d490' WHERE id='51549a8e-918e-4cc3-ad21-ffd4ead0a74e';
UPDATE PROJECTS SET pool_id='37e433e0-a472-417c-a236-0eec96f64376' WHERE id='0e0dd21a-d948-4212-aaae-dedb5f8efb8d';
UPDATE PROJECTS SET pool_id='1b8c769f-0e1f-4618-aeaf-f399a91055b7' WHERE id='d347be4c-eddc-4d9d-9fd8-4bbd24d3e13b';
"""  #  noQA


def data_upgrade():
    """Update data."""

    # Set Default Pool in Project
    op.execute(UPDATES)

    for project_id in PROJECT_DELIVERY_CONFIG:
        config = PROJECT_DELIVERY_CONFIG[project_id]
        archive = config['archive']
        gdrive = config['delivery']
        info = {
            'approve': {
                'archive': {
                    'driver': 'gdrive',
                    'parentId': archive,
                    'subfolders': True,
                    'images': True,
                    'other': True,
                    'name': 'order.customer_order_id',
                    'resize': []
                },
                'gdrive': {
                    'driver': 'gdrive',
                    'parentId': gdrive,
                    'subfolders': False,
                    'images': True,
                    'other': False,
                    'name': 'order.customer_order_id',
                    'resize': []
                },
            }
        }
        if archive == '0BwrdIL719n7wSnVKX05iOUlCdlU':
            info['accept'] = {
                'sftp': {
                  'driver': 'sftp',
                  'subfolders': False,
                  'images': True,
                  'other': False,
                  'name': 'order.customer_order_id',
                  'resize': [
                    {
                        'name': 'resized', 'filter': {'maxbytes': 4000000}}
                  ]
                }
              }

        stmt = """UPDATE PROJECTS SET delivery='{info}' WHERE id='{project_id}';""".format(
            info=json.dumps(info),
            project_id=project_id
        )
        print(stmt)
        op.execute(stmt)


def upgrade():
    """Upgrade database model."""
    op.add_column(
        'projects', sa.Column('pool_id', types.UUIDType(), nullable=True)
    )
    op.add_column(
        'projects', sa.Column('delivery', types.JSONType(), nullable=True),
    )
    op.create_index(
        op.f('ix_projects_pool_id'), 'projects', ['pool_id'], unique=False
    )
    op.create_foreign_key(
        None, 'projects', 'pools', ['pool_id'], ['id']
    )
    op.add_column(
        'projects_version',
        sa.Column('pool_id', types.UUIDType(), autoincrement=False, nullable=True)
    )
    op.add_column(
        'projects_version', sa.Column('delivery', types.JSONType(), nullable=True),
    )
    op.create_index(
        op.f('ix_projects_version_pool_id'), 'projects_version', ['pool_id'], unique=False
    )
    data_upgrade()


def downgrade():
    """Downgrade database model."""
    op.drop_index(op.f('ix_projects_version_pool_id'), table_name='projects_version')
    op.drop_column('projects_version', 'pool_id')
    op.drop_column('projects_version', 'delivery')
    op.drop_index(op.f('ix_projects_pool_id'), table_name='projects')
    op.drop_column('projects', 'pool_id')
    op.drop_column('projects', 'delivery')

