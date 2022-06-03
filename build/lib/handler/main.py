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
        for files in [x[0] for x in os.walk(self.cwd, topdown=False)]:
                d[os.path.join(self.cwd, files)] = {1 if re.search(self.FIN, i) is not None \
                    else -1 if re.search(self.INI, i) is not None else 0 for i in os.listdir(os.path.join(self.cwd, files))}
        # print(d)
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
        self._origin = self.origin
        self.position = {"row":1,"col":1}
        self._block_format = self.block_format
        self._values_format = self.values_format

    @property
    def block_format(self):
        return  self.wb.add_format({
            "bold": True,
            "border": 1})

    @property
    def values_format(self):
        return self.wb.add_format({
            "num_format":11
        })
                
    @property
    def sheet(self):
        return self._sheet
    
    @sheet.setter
    def sheet(self, sheet):
        self._sheet = self.wb.add_worksheet(sheet)
        
    @property
    def origin(self):
        Position = namedtuple("origin", ["row", "col"])
        return Position(1, 1)

    def cells_num(self, text):
        return round(len(text)/self.DEFAULT_CELL_SIZE)

    def cell_size(self, text):
        return round(self.DEFAULT_CELL_SIZE*len(text)/self.DEFAULT_CELL_SIZE)
        
    def write_block(self, block, shift):
        self.position["row"], self.position["col"] = 1, 1
        self.position["col"] += 5*shift
        self.sheet.write(self.position["row"], self.position["col"], block)
        self.position["row"]+=2

    def write_kval(self, key, values, shift):
        self.sheet.write(self.position["row"], self.position["col"], "M/Z/O/E")
        self.sheet.write(self.position["row"], self.position["col"]+1, key)
        for r, lvalue in enumerate(values, start=1):
            self.position["row"]+=1
            for c, value in enumerate(lvalue, start=0):
                self.sheet.write(self.position["row"] , self.position["col"]+c, value, self.values_format)
        self.position["row"]+=2
        
