from . import load_options
import os
import re
# import time
# from colorama import Back

class Handler:
    INI = r"\w+\.ini"
    FIN = r"\.FIN"
    LOG_FILE:str

    def __init__(self, files=None):
        self.cwd = os.getcwd()
        self.dir= os.path.dirname(__file__)
        self.config = load_options()
        self.files = [] if files is None else files

    @property
    def check_folders(self):
        d: dict = {}
        for files in os.listdir(self.cwd):
                d[os.path.join(self.cwd, files)] = [1 if re.search(self.FIN, i) is not None \
                    else -1 if re.search(self.INI, i) is not None else 0 for i in os.listdir(os.path.join(self.cwd, files))]
        return d

class Extracter(Handler):
    def __init__(self):
        super().__init__(self)

class FIN_file(Extracter):
    def __init__(self):
        return

class REZ_file(Extracter):
    def __init__(self):
        return
