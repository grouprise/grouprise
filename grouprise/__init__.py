import os
import subprocess

__version__ = '4.1.0'

try:
    _local_dir = os.path.dirname(__file__)
    __release__ = subprocess.check_output(
        ['git', 'describe', '--tags'],
        cwd=_local_dir, stderr=subprocess.STDOUT).decode().strip()
except (FileNotFoundError, subprocess.CalledProcessError):
    __release__ = f'v{__version__}'
