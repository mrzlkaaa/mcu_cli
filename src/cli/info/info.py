from distutils.command import check
from typing import Iterable
from . import info_load_options
# from ...handler.main import Extracter
import os
import re
import asyncio
import pathlib
from collections import defaultdict
# import random


class Info:
    CALC_CONFIG = "calculation_config.toml"
    MCU_BAT = r"mcu5\w+\.bat"
    FOLDER_SEARCH = {
        "finished": {
            "files": [
                r".\.FIN$",
            ],
            "statusOK": "Finished",
            "styleOK": "default",

        },
        "inprogress": {
            "files": [
                r".\.MCU",
                r".\.ini"
            ],
            "statusOK": "InProgress",
            "styleOK": "warning",

        },
        "torun": {
            "files": [
                "!calculation_config.toml",
                r"mcu5\w+\.bat"
            ],
            "statusOK": "Avaliable to run",
            "styleOK": "good",
            
        }
    }
    '''
   #* check given folders if everething correct before call mcu .exe
   #* Attributes
   #* ----------
   #*
   #* Methods
   #* ----------
   #*
   '''
    
    def __init__(self):
        self.options: dict = info_load_options() #! dependency

        self.cwd: str = pathlib.Path(os.getcwd())
        self.cwd_name = self.cwd.name
        self.list_dir = [i for i in self.cwd.iterdir() if i.is_dir()]
        self.list_files = [i for i in self.cwd.iterdir() if not i.is_dir()]
        self.folder_tree, self.folder_dirs = self._walk_directory()

        self._torun:list = []
        self._torun_unavaliable:list = []
        self._inprogress:list = []
        self._finished:list = []
        
    @property
    def finished(self):
        return self._finished

    @finished.setter
    def finished(self, val):
        self._finished= val

    @property
    def inprogress(self):
        return self._inprogress

    @inprogress.setter
    def inprogress(self, val):
        self._inprogress= val

    @property
    def torun(self):
        return self._torun

    @torun.setter
    def torun(self, val):
        self._torun = val

    @property
    def torun_unavaliable(self):
        return self._torun_unavaliable

    @torun_unavaliable.setter
    def torun_unavaliable(self, val):
        self._torun_unavaliable = val

    def _walk_directory(self):
        d = dict()
        folders = list()

        d[self.cwd_name] = defaultdict(list)  
        for dir_ in self.list_dir:
            folders.append(dir_)
            for sub_dir in pathlib.Path(dir_).iterdir():
                d[self.cwd_name][dir_.name].append(sub_dir.name)
        
        return d, folders

    # def _modifying_folder_status(self):
    #     return

    def _check_name_in_list(
        self,
        name: str,
        folder_data: pathlib.Path | Iterable
    ) -> list:
        if isinstance(folder_data, pathlib.Path):
            folder_data = [i.name for i in folder_data.iterdir() if not i.is_dir()]
        return list(filter(lambda x: re.search(name, x), folder_data))

    def _check_folder(
        self,
        folder: pathlib.Path,
        check_for: str
    ):  
        '''
        #* Special internal method to check
        #* and classify given folder as follows:
        #*  - InProgress / Finished
        #*  - Avaliable to run
        #*  - Unavaliable to run
        #* Parameters
        #* ----------
        #* folder: pathlib.Path
        #*  folder instance of pathlib.Path
        #* Raises
        #* ----------
        #*
        #* Returns
        #* ----------
        #*
        '''

        query_keys = self.FOLDER_SEARCH[check_for]["files"]
        for i in query_keys:
            if not len(self._check_name_in_list(i, folder)):
                return None
        return self.FOLDER_SEARCH[check_for]["statusOK"], self.FOLDER_SEARCH[check_for]["styleOK"]
            

    def get_folders_status(self) -> list:
        # self.torun.clear()
        # self.progressed.clear()
        res_status = list()

        finished = []
        inprogress = []
        torun = []
        torun_unavaliable = []

        #? is recurrsion what i need????
        for i in self.folder_dirs:

            
            check_finished = self._check_folder(i, "finished")
            if check_finished:
                finished.append(
                    (
                        i.name,
                        *check_finished
                    )
                )
                self.finished.append(
                    i.name,
                )
                continue
            check_progressed = self._check_folder(i, "inprogress")
            if check_progressed:
                inprogress.append(
                    (
                        i.name,
                        *check_progressed
                    )
                )
                self.inprogress.append(
                    i.name,
                )
                continue
            
            check_torun = self._check_folder(i, "torun")
            if check_torun:
                torun.append(
                    (
                        i.name,
                        *check_torun
                    )
                )
                self.torun.append(
                    i.name,
                )
                continue

            torun_unavaliable.append(
                (
                    i.name,
                    "Unavaliable to run",
                    "danger"
                )
            )
            self.torun_unavaliable.append(
                    i.name,
                )

        return [
            *torun,
            *inprogress,
            *finished,
            *torun_unavaliable
        ]

