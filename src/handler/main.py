# from . import load_options
import os
import re
import asyncio
from . import load_options
from collections import defaultdict
from .excel_exporter import Excel_exporter

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
        self.towork_with_files = towork_with_files  #* files are given in defaultdict with paths
        
    def write_file(self, parent_path, file, content):
        try:
            with open(os.path.join(parent_path, file), "w", errors='ignore') as f:
                f.writelines(content)
        except Exception as e:
            print(e)

    def read_file(self, parent_path, file):
        try:
            with open(os.path.join(parent_path, file), "r", errors='ignore') as f:
                for row in f:
                    yield row
        except FileNotFoundError as fnfe:
            print(fnfe)
        except Exception as e:
            print(e)

class Extracter(Handler): #todo must takes file, dirs from Info interface!
    
    def __init__(self, towork_with_files:str, code:str):
        super().__init__(towork_with_files)
        self.code = code.upper()   #* what exactly to extract (flux, rates and so on)
        self.data_blocks = dict()  #*  data stores in dict which expands to defaultdict depends on handling file

    def convert_val_to_float(self, value):
        try:
            value = float(value)
            return value
        except ValueError:
            return value

    def convert_arr_to_float(self, arr):
        return list(map(self.convert_val_to_float, arr))

    def excel_writer(self, name):
        return Excel_exporter(file_name=f"{name}.xlsx")

    async def run(self):
        background_tasks = []
        for path, files in self.towork_with_files.items():
            key_folder = os.path.split(path)[-1]
            self.data_blocks[key_folder] = defaultdict(list)
            print(path, key_folder, files)
            background_task = asyncio.create_task(self.extract_method(path, key_folder, files))
            background_tasks.append(background_task)
        await asyncio.gather(*background_tasks)
        self.export_method() #*  writes data to excel file