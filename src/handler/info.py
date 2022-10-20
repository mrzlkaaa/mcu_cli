from . import info_load_options
from .main import Extracter
import os
import re
import asyncio
# import random


class Info:
    def __init__(self):
        self.options: dict = info_load_options()
        self.cwd: str = os.getcwd()
        self.files_list: list = os.listdir() 
        self._dir_list: list = self.get_dir_list()
        self._paths_todirs: list = self.make_todirs_path()
        self.onrun:set = set()
        self.inprogress:set = set()
        self.finished:set = set()
        
    # #* as a test
    @property
    def dir_list(self):
        return self._dir_list

    #* as a test
    @dir_list.setter
    def dir_list(self, dirs):
        self._dir_list = dirs
        self._paths_todirs = self.make_todirs_path()

    @property
    def paths_todirs(self):
        return self._paths_todirs

    def get_dir_list(self):
        return [i for i in self.files_list if os.path.isdir(os.path.join(self.cwd, i))]

    def make_todirs_path(self):
        return [os.path.join(self.cwd, i) for i in self.dir_list]
    
    def check_isinprogress(self, file):
        match = re.search(fr"{self.file_inprogress}\Z", file)
        if match is None:
            return False
        return True

    def check_isfinished(self, file):
        #* check if there is .txt log file
        match_txt = re.search(fr"{self.file_finished[0]}\Z", file)
        
        if match_txt is not None:
            f = Extracter(os.getcwd(), "None").read_file(file)
            for i in f:
                if self.key_word_finished in i:
                    return True
        match_fin = re.search(fr"{self.file_finished[1]}\Z", file)

        if match_fin is not None:
            return True

        return False

    #* this three func below are to append sets during folder check
    def add_calcs_onrun(self, folder):
        return self.onrun.add(folder)
    
    def add_calcs_inprogress(self, folder):
        return self.inprogress.add(folder)

    def add_calcs_finished(self, folder):
        return self.finished.add(folder)

    def main(self):
        return

class MCU(Info):
    def __init__(self):
        super().__init__()
        self.file_inprogress: str = self.options["mcu"]["status"]["inprogress"]["file"]
        self.file_finished: list = self.options["mcu"]["status"]["finished"]["file"]
        self.key_word_finished: str = self.options["mcu"]["status"]["finished"]["key_word"]

    async def check_folder(self, path):
        for i in os.listdir(path):
            os.chdir(path)
            toadd_folder = os.path.split(os.getcwd())[-1]
            if self.check_isfinished(i):
                self.add_calcs_finished(toadd_folder)
                break
            elif self.check_isinprogress(i):
                self.add_calcs_inprogress(toadd_folder)
                break
        await asyncio.sleep(0.001)
        
    async def calc_status(self):
        tasks:list = []
        for i in self.paths_todirs:
            task = asyncio.create_task(self.check_folder(i))
            tasks.append(task)

        await asyncio.gather(*tasks)

        for i in set(self.dir_list).difference({*self.inprogress, *self.finished}):
            self.add_calcs_onrun(i)
            
        os.chdir(self.cwd)