"""Storage adapters for briefy.leica."""


class Storage:
    """Storage."""

    def __init__(self, url, payload=None):
        """Initialize storage."""
        self.url = url
        self.payload = payload

    def load(self):
        """Load."""
        raise NotImplementedError

    def save(self):
        """Save."""
        raise NotImplementedError


from .s3 import S3Storage  # noQA
