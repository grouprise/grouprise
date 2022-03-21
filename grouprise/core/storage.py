import os.path
import secrets
import string
from pathlib import Path

from django.core.files.storage import FileSystemStorage


class Storage(FileSystemStorage):
    FILE_ROOT_LENGTH = 16

    def get_available_name(self, name, max_length=None):
        dir_name, file_name = os.path.split(name)
        # normalize the file extension to lower case
        file_ext = os.path.splitext(file_name)[1].lower()
        result = None
        while result is None:
            alphabet = string.ascii_lowercase + string.digits
            file_root = "".join(
                secrets.choice(alphabet) for _ in range(self.FILE_ROOT_LENGTH)
            )
            result = Path(dir_name) / f"{file_root}{file_ext}"
            if self.exists(result):
                result = None
        return str(result)
