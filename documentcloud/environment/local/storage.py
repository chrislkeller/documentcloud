"""
This is an incomplete implementation of the Storage abstraction
for the local filesystem.  This is only used during tests and implements
what is needed for the tests which use it.

A more complete abstraction is possible, but deemed unecessary as using MinIO
is the preferred development environment
"""
# Django
from django.conf import settings

# Standard Library
import os
from pathlib import Path

# Third Party
import environ

env = environ.Env()


class LocalStorageFile:
    def __init__(self, storage_system, fn, mode="w"):
        self.storage = storage_system
        self.filename = os.path.join(settings.MEDIA_ROOT, fn)
        self.mode = mode
        self.handle = None

    def __enter__(self):
        # Ensure that the path exists if writing
        if self.mode.startswith("w"):
            path = Path(self.filename)
            path.parent.mkdir(parents=True, exist_ok=True)
        self.handle = open(self.filename, self.mode)
        return self.handle

    def __exit__(self, exception_type, exception_value, traceback):
        if self.handle is not None:
            self.handle.close()

        if self.storage.trigger is not None:
            self.storage.trigger(self.filename)


class LocalStorage:
    def __init__(self, trigger=None):
        self.trigger = trigger

    # pylint: disable=invalid-name
    @staticmethod
    def size(filename):
        return os.path.getsize(os.path.join(settings.MEDIA_ROOT, filename))

    def open(self, filename, mode="w"):
        return LocalStorageFile(self, filename, mode)


storage = LocalStorage()