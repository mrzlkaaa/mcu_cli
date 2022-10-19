from . import load_options
from colorama import Fore
from tabulate import tabulate
from handler.main import Handler
from handler.info import MCU
from handler.run import Run
from handler.extracter_fin import Fin
from handler.clear import Clear
from handler.copy import Copy
import fire
import os
import re
import asyncio
import inspect



class Prettier():
    bcolors = {
        "HEADER": Fore.MAGENTA,
        "OKGREEN" : Fore.GREEN,
        "OKCYAN" : Fore.CYAN,
        "WARNING" : Fore.YELLOW,
        "FAIL" : Fore.RED,
        "RESET" : Fore.RESET,
    }
    # def __init__(self):

    def colorize(self, string, type, rnge=None):
        if rnge is None:
            return f"{self.bcolors[type]}{string}{self.bcolors['RESET']}"
        formatted_iterable: list = []
        for _ in range(len(rnge)):
            formatted_iterable.append(f"{self.bcolors[type]}{string}{self.bcolors['RESET']}")
        return formatted_iterable


class CLI:
    STATUS_HEADER:list = ["Folder", "Status"]
    
    def __init__(self, filename=None, mpi=None): #todo move args to func?
        self.options = load_options()
        self.prettier = Prettier()
        self.file_name = self.options["DEFAULT_NAME_PATTERN"] if filename is None else filename
        self.mpi = 1 if mpi is None else mpi
        # self.mcu_info = self.get_status_info()
        self.mcu_info = MCU()
        
    
    def __repr__(self):
        return "use < mcu help > to see avaliable commands >"

    def key_filter(self, key, folders):
        try:
            return list({i for i in folders for j in key if i==re.search(r"[^\\.].*[^\\]", j).group()})
        except AttributeError:
            print("Folder with a given name is not found")

    async def get_status_info(self):
        await self.mcu_info.calc_status()
        print("folders checked")
        
    
    async def status(self):
        await self.get_status_info()
        folder, status = list(map(lambda x: self.prettier.colorize(x, "HEADER"), self.STATUS_HEADER))
        return print(tabulate({
                            folder:[
                                *self.mcu_info.onrun, *self.mcu_info.inprogress, *self.mcu_info.finished
                            ],
                            status:[
                                *self.prettier.colorize("ONRUN", "FAIL", self.mcu_info.onrun),
                                *self.prettier.colorize("INPROGRESS", "OKCYAN", self.mcu_info.inprogress),
                                *self.prettier.colorize("FINISHED", "OKGREEN", self.mcu_info.finished)
                            ]},
                            headers = "keys",
                            tablefmt="pretty"))

    async def run(self, *key):
        await self.get_status_info()
        onrun:list = self.mcu_info.onrun
        if len(key)>0:
            onrun = self.key_filter(key, self.mcu_info.onrun)
        Run(self.file_name, onrun, self.mpi).run()

    async def restart(self, *key):
        await self.get_status_info()
        onrun = [*self.mcu_info.inprogress, *self.mcu_info.finished]
        if len(key)>0:
            onrun = self.key_filter(key, onrun)
        Run(self.file_name, onrun, self.mpi).run()

    async def extract(self, *key, **params):
        await self.get_status_info()
        onclear:list = self.mcu_info.finished
        code, extension = params["code"], params["extension"]
        if len(key)>0:
            onclear = self.key_filter(key, self.mcu_info.finished)
        background_tasks = set()
        for folder in  onclear: #* loop over folder and all .FIN files
            folder_path = os.path.join(os.getcwd(), folder)
            fin = Fin(code, folder_path, extension, self.file_name) #* FIN instance for each iterable folder
            task = asyncio.create_task(fin.extract_method())
            background_tasks.add(task)
        res = await asyncio.gather(*background_tasks)
        print(res)
        
    async def clear(self, *key):
        await self.get_status_info()
        if not len(key)>0:
            raise TypeError("No keys to clear given")
        onclear = self.key_filter(key, self.mcu_info.finished)
        Clear(self.file_name, onclear, self.mpi).clear()
    
    async def copy(self, *key):
        await self.get_status_info()
        oncopy:list = self.mcu_info.dir_list
        if len(key)>0:
            oncopy = self.key_filter(key, self.mcu_info.dir_list)
        folders_path = Copy.folders_to_paths(oncopy)
        Copy(folders_path, self.mcu_info.options["mcu"]["tocopy"]["files"]).copy()
        

        return

    def help(self):
        return "List of avaliable commands:\n\
        < status > - shows calculations status in folders of current directory\n\
        < clear arg1 arg2 ... > - initiates folders cleaning (removes files created by software run);\n\
        if arguments omitted will clear all folders\n\
        < run arg1 arg2 ... > - run calculations in folders of current directory;\n\
        if arguments omitted will run calculations in all folders\n"


def initiate():
    asyncio.run(fire.Fire(CLI))

if __name__ == "__main__":
    initiate()


    