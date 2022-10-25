# from . import load_options
import os
import re
from . import load_options

# import time
# from colorama import Back

class Handler:
    INI = r"\w+\.ini"
    FIN = r"\.FIN"
    LOG_FILE:str

    def __init__(self, towork_with_files):
        self.cwd = os.getcwd() #?
        self.dir= os.path.dirname(__file__) #?
        self.config = load_options()
        self.towork_with_files = towork_with_files #* files are given in defaultdict with paths

    @property
    def check_folders(self):
        d: dict = {}
        for files in [x[0] for x in os.walk(self.cwd)]:
            if not files == self.cwd:
                d[os.path.join(self.cwd, files)] = {1 if re.search(self.FIN, i) is not None \
                    else 0 if re.search(self.INI, i) is not None else -1 for i in os.listdir(os.path.join(self.cwd, files))}
        # print(d)
        return d

class Extracter(Handler): #todo must takes file, dirs from Info interface!
    
    def __init__(self, towork_with_files:str, code:str):
        super().__init__(towork_with_files)
        self.code = code.upper()  #* what exactly to extract (flux, rates and so on)


    def read_file(self, parent_path, file):
        try:
            with open(os.path.join(parent_path, file), "r", errors='ignore') as f:
                for row in f:
                    yield row
        except FileNotFoundError as fnfe:
            print(fnfe)
        except Exception as e:
            print(e)

        
