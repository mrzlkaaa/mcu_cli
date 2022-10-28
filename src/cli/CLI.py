from . import load_options
from colorama import Fore
from tabulate import tabulate
from handler.main import Handler
from handler.info import MCU
from handler.run import Run
from handler.extracter_fin import Fin
from handler.extracter_rez import Rez
from handler.clear import Clear
from handler.copy import Copy
from handler.filter import Filter
from handler.post_processing import Post_processing
import __main__
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
        
    
    # def __repr__(self):
    #     return "use < mcu help > to see avaliable commands >"

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
        onrun_paths = [self.mcu_info.make_todir_path(i) for i in onrun]
        print(self.file_name)
        Run(self.file_name, onrun_paths, self.mpi).run()

    async def restart(self, *key):
        await self.get_status_info()
        onrun = [*self.mcu_info.inprogress, *self.mcu_info.finished]
        if len(key)>0:
            onrun = self.key_filter(key, onrun)
        onrun_paths = [self.mcu_info.make_todir_path(i) for i in onrun]
        Run(self.file_name, onrun_paths, self.mpi).run()

    async def post_processing(self, *key, **params):
        code = params["code"]
        await self.get_status_info()
        onclear:list = self.mcu_info.finished
        if len(key)>0:
            onclear = self.key_filter(key, self.mcu_info.finished)
        onclear_paths = [self.mcu_info.make_todir_path(i) for i in onclear]
        filtered = Filter(onclear_paths, "byregex", 'DAT\\Z|FIN_B\\d+').filter()
        filtered = Filter(filtered, "byregex", 'DAT\\Z').filter()
        Post_processing(filtered, code).DAT_edit_run()

    async def extract_fin(self, *key, **params):
        code = params["code"]
        await self.get_status_info()
        onclear:list = self.mcu_info.finished
        if len(key)>0:
            onclear = self.key_filter(key, onclear)
        onclear_paths = [self.mcu_info.make_todir_path(i) for i in onclear]
        filtered = Filter(onclear_paths, "byregex", 'FIN\\Z|FIN_B\\d+').filter()
        print(filtered)
        await Fin(filtered, code).run()
        
    async def extract_rez(self, *key, **params):  #todo method under development
        code = params["code"]
        await self.get_status_info()
        onclear:list = self.mcu_info.finished
        if len(key)>0:
            onclear = self.key_filter(key, onclear)
        onclear_paths = [self.mcu_info.make_todir_path(i) for i in onclear]
        filtered = Filter(onclear_paths, "byregex", 'REZ\\Z').filter()
        print(filtered)
        await Rez(filtered, code).run()

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
            oncopy = self.key_filter(key, oncopy)

        oncopy_paths = [self.mcu_info.make_todir_path(i) for i in oncopy]

        patterns = [
            *[fr"{extension}\Z|{extension}_B\d+" for extension in self.mcu_info.options["mcu"]["tocopy"]["files"]],
            *self.mcu_info.options["mcu"]["filter"]["regex"]
        ]
        filtered = Filter(oncopy_paths, "byregex", *patterns).filter()
        print(filtered)
        Copy(filtered).copy_as_defaultdict()

        return

    async def help(self):
        return "List of avaliable commands:\n\
        < status > - shows calculations status in folders of current directory\n\
        < clear arg1 arg2 ... > - initiates folders cleaning (removes files created by software run);\n\
        if arguments omitted will clear all folders\n\
        < run arg1 arg2 ... > - run calculations in folders of current directory;\n\
        if arguments omitted will run calculations in all folders\n"


def initiate():
    # t = asyncio.create_task(fire.Fire(CLI))
    # print(fire.Fire(CLI))
    fire.Fire(CLI)
    # await t

# if __name__ == "__main__":
#     print("CALLED")
#     initiate()


    