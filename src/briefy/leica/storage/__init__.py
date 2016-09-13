class Storage:
    def __init__(self, url, payload=None):
        self.url = url
        self.payload = payload

    def load(self):
        raise NotImplementedError

    def save(self):
        raise NotImplementedError


from .s3 import S3Storage  #noQA
