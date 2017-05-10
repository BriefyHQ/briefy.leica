"""Reports in CSV."""
from briefy.ws.resources import BaseResource
from datetime import datetime
from io import StringIO
from pyramid.request import Response

import csv
import newrelic.agent


class BaseReport(BaseResource):
    """Reports in CSV."""

    model = None
    filename = ''
    mime_type = 'text/csv'
    column_order = ()

    def __init__(self, context, request):
        """Initialize the report view."""
        super().__init__(context, request)
        newrelic.agent.set_background_task(flag=True)

    @staticmethod
    def _format_datetime(raw_value: datetime, timezone, as_local: bool=False) -> str:
        """Return a string representation of a datetime value."""
        value = ''
        if raw_value:
            value = raw_value
            if as_local:
                value = value.astimezone(timezone)
            value = value.isoformat()
        return value

    def convert_data(self, data: object):
        """Apply some basic type conversions."""
        raise NotImplementedError('Need to be implemented by subclass')

    def default_filters(self, query) -> object:
        """Default filters to be applied to every query.

        This is supposed to be specialized by resource classes.
        :returns: A tuple of default filters to be applied to queries.
        """
        raise NotImplementedError('Need to be implemented by subclass')

    def get_report_data(self, filename: str):
        """Execute the report, return a tuple with data and metadata."""
        content_type = self.mime_type
        query = self.default_filters(self.model.query())
        results = query.all()
        csv_file = StringIO()
        header = [c for c in self.column_order]
        writer = csv.DictWriter(csv_file, fieldnames=header, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        for row in results:
            row = self.convert_data(row)
            writer.writerow(row)
        data = csv_file.getvalue()
        return filename, content_type, data

    def get_response(self, filename, content_type, data):
        """Prepare the response."""
        response = Response()
        header_list = [
            ('Content-Disposition', 'attachment; filename={filename}'.format(
                filename=filename
            )),
            ('Pragma', 'no-cache'),
            ('Expires', 'Fri, 29 Mar 2012 17:30:00 GMT'),
        ]

        response.status_int = 200
        response.charset = 'utf-8'
        response.content_type = content_type
        response.text = data
        response.headerlist = header_list
        return response

    def get(self) -> Response:
        """Return CSV with reports."""
        filename = self.filename
        filename, content_type, data = self.get_report_data(filename)

        return self.get_response(filename, content_type, data)
