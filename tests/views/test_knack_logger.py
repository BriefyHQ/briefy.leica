"""Test knack logger view."""
import json
import pytest


@pytest.mark.usefixtures('login')
class TestAssetImportView():
    """Test AssetImportService view."""

    base_path = '/knack/logger'
    referrer = 'http://localhost:8080/tests/views/test_knack_logger'

    @property
    def headers(self):
        return {
            'X-Locale': 'en_GB',
            'Referrer': self.referrer,
            'Authorization': 'JWT {token}'.format(token=self.token)
        }

    def test_post_knack_logger_success(self, app):
        """Test valid post to knack logger endpoint."""
        payload_dict = dict(name='value', foo='bar')
        payload = json.dumps(payload_dict)
        request = app.post('{base}'.format(base=self.base_path),
                           payload, headers=self.headers, status=200)

        assert 'application/json' == request.content_type
        result = request.json

        assert result['status'] == 'success'

    def test_post_knack_logger_failure(self, app):
        """Test invalid post to knack logger endpoint"""
        payload = 'foo=bar'
        request = app.post('{base}'.format(base=self.base_path),
                           payload, headers=self.headers, status=400)

        assert 'application/json' == request.content_type
        result = request.json

        assert result['status'] == 'error'
