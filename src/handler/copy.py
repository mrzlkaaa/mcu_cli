from .filter import Filter
from collections import defaultdict
import re
import os
import shutil

class Copy:
    COPY_FOLDER_NAME = "!COPIES"
    def __init__(self, tocopy_files):
        self.tocopy_files = tocopy_files

    @classmethod
    def single_extension(cls, paths, extension):
        return cls(paths, [extension])

    def create_folder(self, path):
        try:
            os.mkdir(path)
        except FileExistsError:
            raise FileExistsError(f"Fodler <{os.path.split(path)[-1]}> already exists")
        except FileNotFoundError as e:
            raise e

    def copy_as_defaultdict(self):
        copies_dst = os.path.join(os.getcwd(), self.COPY_FOLDER_NAME)
        self.create_folder(copies_dst)

        for k,v in self.tocopy_files.items():
            folder = os.path.split(k)[-1]
            dst_folder = os.path.join(copies_dst, "!" + folder)
            self.create_folder(dst_folder)
            for file in v:
                source = os.path.join(k,file)
                dst = os.path.join(dst_folder, file)
                shutil.copy2(source, dst)
        return
