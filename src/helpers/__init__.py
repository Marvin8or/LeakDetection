import os
import errno
import json
from .report_email import *
from pathlib import Path

class JsonFile(dict):

    def __init__(self, path, *args, **kwargs):
        verify = kwargs.pop("verify", False)
        self.path = Path(path)

        if not self.path.is_file() or verify:
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), path)
        
        else:
            self.read()


    def read(self):
        """
        Read data from file.
        """
        self.clear()
        with self.path.open() as fp:
            self.update(json.load(fp, object_pairs_hook=dict))

    def write(self, sort_keys=False):
        """
        Write data to file (overwrite), create file if it does not exist.
        """
        with self.path.open("w+", encoding="utf-8", newline="\n") as fp:
            json.dump(self, fp, indent=4, sort_keys=sort_keys)


