import os.path
import random
import string
from pathlib import Path

from django.core.files.storage import FileSystemStorage


class Storage(FileSystemStorage):
    FILE_ROOT_LENGTH = 16
    VALID_CHARACTERS = string.ascii_lowercase + string.digits

    def get_available_name(self, name, max_length=None):
        dir_name, file_name = os.path.split(name)
        # normalize the file extension to lower case
        file_ext = os.path.splitext(file_name)[1].lower()
        result = None
        while result is None:
            file_root = "".join(
                random.choices(self.VALID_CHARACTERS, k=self.FILE_ROOT_LENGTH)
            )
            result = Path(dir_name) / f"{file_root}{file_ext}"
            if self.exists(result):
                result = None
        return str(result)
