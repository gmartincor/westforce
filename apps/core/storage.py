from django.contrib.staticfiles.storage import ManifestStaticFilesStorage
from whitenoise.storage import CompressedManifestStaticFilesStorage


class MissingFileManifestStaticFilesStorage(CompressedManifestStaticFilesStorage):
    manifest_strict = False
    
    def hashed_name(self, name, content=None, filename=None):
        try:
            return super().hashed_name(name, content, filename)
        except ValueError:
            return name
