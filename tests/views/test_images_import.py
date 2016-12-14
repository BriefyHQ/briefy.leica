"""Test assets view."""
from briefy.leica import models

import csv
import json
import pytest
import os


@pytest.mark.usefixtures('db_transaction', 'create_dependencies')
class TestAssetImportView():
    """Test AssetImportService view."""

    base_path = '/knack/assets/import'

    dependencies = [
        (models.Professional, 'data/professionals.json'),
        (models.Customer, 'data/customers.json'),
        (models.Project, 'data/projects.json'),
        (models.JobOrder, 'data/job_orders.json'),
        (models.JobAssignment, 'data/jobs.json')
    ]

    @property
    def headers(self):
        return {'X-Locale': 'en_GB'}

    def test_post_import_assets(self, app):
        """Test post to the internal import assets."""
        csv_file = open(os.path.join(__file__.rsplit('/', 2)[0], 'data/images_import.csv'))
        asset_rows = csv.DictReader(csv_file)
        params = {'data': []}
        for item in asset_rows:
            params['data'].append(item)
        payload = json.dumps(params)
        request = app.post('{base}'.format(base=self.base_path),
                           payload, headers=self.headers, status=200)

        assert 'application/json' == request.content_type
        result = request.json

        assert result['status'] == 'success'
        assert 'data' in result.keys()
        assert 'created' in result['data'].keys()
        assert 'updated' in result['data'].keys()
        assert 'failed' in result['data'].keys()

        db_assets = models.Asset.query().all()
        assert len(db_assets) == 47
