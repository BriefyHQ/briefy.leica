"""Base report class."""
from briefy.common.db import Base
from briefy.leica.reports import records_to_csv
from io import StringIO
from sqlalchemy.orm.query import Query


class BaseReport:
    """Base report."""

    fieldnames = ()

    @property
    def _query_(self) -> Query:
        """Return the query for this report.

        :return: Query object.
        """
        raise NotImplementedError('Need to be implemented by a subclass')

    @property
    def records(self) -> list:
        """Return the list of records."""
        query = self._query_
        results = query.all()
        return results

    @staticmethod
    def transform(record: Base) -> dict:
        """Transform a record and result a record.

        This should be specialised on subclasses.

        :param record: Object to be transformed.
        :return: Dictionary with data already transformed.
        """
        return record.to_dict()

    def __call__(self) -> StringIO:
        """Execute this report.

        :return: A StringIO buffer with the result.
        """
        raw_records = self.records
        records = []
        for record in raw_records:
            records.append(self.transform(record))
        return records_to_csv(records, self.fieldnames)
