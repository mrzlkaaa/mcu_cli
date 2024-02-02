
import fire
import os
import re
import asyncio
import inspect

import rich
from . import load_options
from colorama import Fore

from .display.display import Display
from .info.info import Info
from .runner.run import Run
from .support.main import clear as clear_folder


def folders_parser(*folders):
    #* pattern for both unix and win
    pattern = r"[^\.\\]+\w+[^\\/]"
    
    parsed_folders = []
    for i in folders:
        res = re.search(
            pattern,
            i
        )
        if res is None:
            raise TypeError(f"Cannot parse {i}")
        parsed_folders.append(res.group(0))
    return parsed_folders

class CLI:
    STATUS_HEADER:list = ["Folder", "Status"]
    '''
    #* CLI interface to interact with / manage
    #* MCU files via command prompt
    #* This interface includes following packages
    #*  Info - to get information / current status in folders
    #*  Display - to display information in command prompt
    #*  Extract
    #*  Run    
    #* Parameters
    #* ----------
    #*
    #* Raises
    #* ----------
    #*
    #* Returns
    #* ----------
    #*
    '''
    
    def __init__(
        self,
        folders:tuple | None = None,
        mpi=None
    ): #todo move args to func?
        self.folders = folders
        self.mpi = 1 if mpi is None else mpi
        self.display = Display() #! dependency
        self.info = Info() #! dependency
        self.options = load_options() #! dependency

        self.folders_status = self.info.get_folders_status()
        

    def folders_status(func):
        def wrapper(self, *args, **kwargs):
            
            #* kepp folders status up to date
            #* each request updates
            #* self.info.torun and self.info.progressed
            self.info.get_folders_status()
            func(self, *args, **kwargs)
            
        return wrapper


    def _str_match(self, string:str):
        match string:
            case "finished":
                return self.info.finished
            case "inprogress":
                return self.info.inprogress
            case "torun":
                return self.info.torun
            case _:
                raise ValueError(f"Given string < {string} > not found among exising cases")
    
    def args_parse(folders_type:str | None = None):
        
        def wrap(func):
            def wrapped(self, *args, **kwargs):
                folders = self._str_match(folders_type)
                if len(args) > 0:
                    args = folders_parser(*args)
                    intersected_folders = list(
                        set(folders).intersection(set(args))
                    )
                    if not len(intersected_folders) > 0:
                        return print(f"Among given folders there are no one classified as < {folders_type} >")
                        
                    return func(self, *intersected_folders, **kwargs)
                elif not len(folders) > 0:
                    return print(f"There are no folders classified as < {folders_type} >")
                func(self, *folders, **kwargs)
                
            return wrapped
        return wrap


    def key_filter(self, key, folders):
        try:
            return list({i for i in folders for j in key if i==re.search(r"[^\\.].*[^\\]", j).group()})
        except AttributeError:
            print("Folder with a given name is not found")
        
    def get_tree(self):
        tree = self.info.folder_tree
        self.display.tree(tree)
        

    def get_folders_status(self):
        self.display.table(cols=self.STATUS_HEADER, rows_data=self.folders_status)

    
    @args_parse("torun")
    def run(
        self, 
        *folders: tuple
    ):
        '''
        #* Promt command to initiate
        #* mcu code calculations  
        #* Parameters
        #* ----------
        #*
        #* Raises
        #* ----------
        #*
        #* Returns
        #* ----------
        #*
        '''
        #! dev mode!
        dev=0
        if dev:
            r = Run(
                display=self.display, #! dont like it
                folders=[
                    # "f1", 
                    # "f2", 
                    "f3", 
                    # "f5"
                ],
                dev_path="/mnt/c/Users/Nikita/Desktop/codes/mcu_code_runner/src/cli/runner/test_data",
                cpu_number=self.mpi
            )
            asyncio.run(r.call())
            return
        
        folders = list(folders)
        r = Run(
            display=self.display, #! dont like it
            folders=folders,
            cpu_number=self.mpi
        )
        
        asyncio.run(r.call())
        
        return

    @args_parse("torun")
    def run_chain(
        self, 
        *folders: tuple,
        cpu_max:int | None
    ):
        '''
        #* Promt command to initiate
        #* mcu code calculations  
        #* Parameters
        #* ----------
        #*
        #* Raises
        #* ----------
        #*
        #* Returns
        #* ----------
        #*
        '''
        folders = list(folders)
        Run.call_chain(
            folders_chain=folders,
            display=self.display, #! dont like it
            cpu_number=self.mpi,
            cpu_max=cpu_max,
        )
        
        return

    @args_parse("inprogress")
    def restart_chain(
        self, 
        *folders: tuple,
        cpu_max:int | None
    ):
        '''
        #* Promt command to initiate
        #* mcu code calculations  
        #* Parameters
        #* ----------
        #*
        #* Raises
        #* ----------
        #*
        #* Returns
        #* ----------
        #*
        '''
        folders = list(folders)
        Run.call_chain(
            folders_chain=folders,
            display=self.display, #! dont like it
            cpu_number=self.mpi,
            cpu_max=cpu_max,
            with_restart=True
        )
        
        return

    @args_parse("inprogress")
    def restart(
        self, 
        *folders: tuple,
    ):
        dev=0
        if dev:
            r = Run(
                display=self.display, #! dont like it
                folders=[
                    # "f1", 
                    # "f2", 
                    "f3", 
                    # "f5"
                ],
                dev_path="/mnt/c/Users/Nikita/Desktop/codes/mcu_code_runner/src/cli/runner/test_data",
                cpu_number=self.mpi,
                restart=True
            )
            asyncio.run(r.call())
            return
        
        folders = list(folders)    
        r = Run(
            display=self.display, #! dont like it
            folders=folders,
            cpu_number=self.mpi,
            restart=True
        )
    
        asyncio.run(r.call())
        
        
    @args_parse("inprogress")
    def clear(
        self,
        *folders:tuple
    ):
        print(folders)
        cwd = os.getcwd()
        for folder in folders:
            clear_folder(
                os.path.join(
                    cwd,
                    folder
                )
            )
        
        return


def initiate():
    # print(fire.Fire(CLI))
    fire.Fire(CLI)

if __name__ == "__main__":
    print("CALLED")
    # asyncio.run(initiate())


    