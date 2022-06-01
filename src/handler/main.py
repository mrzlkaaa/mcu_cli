# from . import load_options
import os
import re
import xlsxwriter
from collections import namedtuple 
# import time
# from colorama import Back

class Handler:
    INI = r"\w+\.ini"
    FIN = r"\.FIN"
    LOG_FILE:str

    def __init__(self, files=None):
        self.cwd = os.getcwd()
        self.dir= os.path.dirname(__file__)
        # self.config = load_options()
        self.files = [] if files is None else files

    @property
    def check_folders(self):
        d: dict = {}
        for files in os.listdir(self.cwd):
                d[os.path.join(self.cwd, files)] = {1 if re.search(self.FIN, i) is not None \
                    else -1 if re.search(self.INI, i) is not None else 0 for i in os.listdir(os.path.join(self.cwd, files))}
        return d

class Extracter(Handler):
    
    def __init__(self, folder_path:str, extension:str, file_name:str=None):
        super().__init__()
        self.folder_path:str = folder_path
        self.extension:str = fr".{extension}\Z"
        self.files:list = self.find_files
        self.file:list = self.match_file(file_name) if file_name is not None else self.files

    @property
    def find_files(self): #* looping in folder_path and collecting files with .<<extension>>
        return [i for i in os.listdir(self.folder_path) if re.search(self.extension, i)]

    def match_file(self, file_name):
        file: list = [i for i in self.find_files if file_name in i]
        if not len(file) > 0:
            raise FileNotFoundError("File with a given name is not found")
        return file

    def read_file(self, itr):
        try:
            # for i in self.file:
                # print(i)
            with open(os.path.join(self.folder_path, itr), "r", errors='ignore') as f:
                for row in f:
                    yield row
        except FileNotFoundError as fnfe:
            print(fnfe)
        except Exception as e:
            print(e)

class Excel_exporter():
    DEFAULT_CELL_SIZE = 8
    def __init__(self, **kwargs):
        self.wb = xlsxwriter.Workbook(kwargs.get("file_name"))
        self._sheet = None
        self.origin = self.positions

    @property
    def sheet(self):
        return self._sheet
    
    @sheet.setter
    def sheet(self, sheet):
        self._sheet = self.wb.add_worksheet(sheet)
        
    @property
    def positions(self):
        Position = namedtuple("origin", ["row", "col"])
        return Position(1, 1)

    def cells_num(self, text):
        return round(len(text)/self.DEFAULT_CELL_SIZE)

    def cell_size(self, text):
        
        return round(len(text)/self.DEFAULT_CELL_SIZE)
        

    def write(self, block, key, value):
        self.sheet.set_column(self.origin.col, self.origin.col
            + self.cell_size(block)) #! not finished
        self.sheet.write(self.origin.row, self.origin.col, block)
        # self.wb.close()
        
