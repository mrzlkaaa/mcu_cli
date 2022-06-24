from . import load_options
from colorama import Fore
from handler.main import Handler
from handler.run import Run
from handler.extracter_fin import Fin
from handler.clear import Clear
import fire
import os
import re
from tabulate import tabulate


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

    def colorize(self, string, type):
        return f"{self.bcolors[type]}{string}{self.bcolors['RESET']}"

class CLI:
    def __init__(self, filename=None, mpi=None): #todo move args to func?
        self.options = load_options()
        self.prettier = Prettier()
        self.file_name = self.options["DEFAULT_NAME_PATTERN"] if filename is None else filename
        self.status_table, self.on_clear, \
            self.on_progress, self.on_run = self.status_formatter(Handler().check_folders) #todo refactor to dict?
        self.mpi = 1 if mpi is None else mpi
    
    def __repr__(self):
        return "use < mcu help > to see avaliable commands >"

    #* creates 2d array that fills by array [folder, status] 
    def status_formatter(self, checked_folders):
        table:list = []
        ok:list = []
        progress: list = []
        bad: list = []
        for k,v in checked_folders.items():
            folder:str = os.path.split(k)[-1]
            if len(v)==3:
                finished:list = [folder, self.prettier.colorize("Finished", "OKGREEN") ]
                table.append(finished)
                ok.append(folder)
            elif len(v)==2:
                inprogress:list = [folder, self.prettier.colorize("InProgress", "OKCYAN")]
                table.append(inprogress)
                progress.append(folder)
            else:
                torun:list = [folder, self.prettier.colorize("ToRun", "FAIL")]
                table.append(torun)
                bad.append(folder)
        
        return table, ok, progress, bad

    def key_filter(self, key, folders):
        try:
            return list({i for i in folders for j in key if i==re.search(r"[^\\.].*[^\\]", j).group()})
        except AttributeError:
            print("Folder with a given name is not found")

    @property
    def status(self):
        headers = ["Folder", "Status"]
        return print(tabulate(self.status_table, 
            headers = map(lambda x: self.prettier.colorize(x, "HEADER"), headers),
            tablefmt="pretty"))

    def run(self, *key):
        if len(key)>0:
            self.on_run = self.key_filter(key, self.on_run)
        Run(self.file_name, self.on_run, self.mpi).run()

    def restart_run(self, *key):
        self.on_run = self.on_progress
        if len(key)>0:
            self.on_run = self.key_filter(key, self.on_run)
        self.run()

    def extract(self, *key, **params):
        if len(key)>0:
            self.on_clear = self.key_filter(key, self.on_clear)
        for folder in  self.on_clear: 
            folder_path = os.path.join(os.getcwd(), folder)
            try:
                code, extension = params["code"], params["extension"]
                Fin(code, folder_path, extension, self.file_name)
                # db.excel_export()
            except KeyError:
                print("Code or extension is not given")
                # return
        
    def clear(self, *key):
        if len(key)>0:
            self.on_clear = self.key_filter(key, self.on_clear)
        Clear(self.file_name, self.on_clear, self.mpi).clear()
    
    def help(self):
        return "List of avaliable commands:\n\
        < status > - shows calculations status in folders of current directory\n\
        < clear arg1 arg2 ... > - initiates folders cleaning (removes files created by software run);\n\
        if arguments omitted will clear all folders\n\
        < run arg1 arg2 ... > - run calculations in folders of current directory;\n\
        if arguments omitted will run calculations in all folders\n"


def initiate():
    fire.Fire(CLI)

if __name__ == "__main__":
    initiate()


    