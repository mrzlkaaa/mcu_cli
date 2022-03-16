import os, sys
import re
import concurrent.futures
import subprocess
import asyncio
import time
from colorama import Back

class Handler:
    INI = r"\w+\.ini"
    FIN = r"\.FIN"
    LOG_FILE = "!log.txt"

    def __init__(self, files:list):
        self.cwd = os.getcwd()
        self.files = files

    @property
    def check_folders(self):
        d: dict = {}
        for root, dirs, files in os.walk(self.cwd):
            if root != self.cwd:
                d[root] = {1 if re.search(self.FIN, i) is not None else 2 if re.search(self.INI, i) is not None else 0 for i in files}
        return d

class Run(Handler):
    MCU_BAT:str = "mcu5.bat"
    MCUMPI_BAT:str = "mcu5mpi.bat"
    BURN:str = r"burn\Z"
    BURN_config = {
         "NTOT",
         "NBAT",
         "MAXS"
    }
    HISTORIES = "Histories"
    FINISHED = {
        "The task is finished.",
        "No burnup in the task (file *.sb not found)"
    }
    
    def __init__(self, files:list, cores:int):
        super().__init__(files)
        self.cores=cores if cores==1 else round(cores/len(self.files))
    
    @property
    def check_finished(self):
        with open(self.LOG_FILE) as f:
            for i in f:
                yield i

    @property
    def get_histories(self):
        history:int = 1
        file_name, *_ = [i for i in os.listdir() if re.search(self.BURN, i)]
        with open(file_name, 'r') as f:
            context = f.readlines()
            history_coefs = [i.split()[-1] for i in context for j in self.BURN_config if j in i]
        for i in history_coefs:
            history *= int(i) 
        return history

    async def async_loop(self):
        proc = await asyncio.create_subprocess_shell(
        self.cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)

        run:bool = True
        last_printed_histories:int
        while run==True:
            try:
                with open(self.LOG_FILE, "r") as f:
                    context = f.readlines()
                printed_histories = [int(i.split()[-1]) for i in context if self.HISTORIES in i]
                last_printed_histories = printed_histories[-1]
                share = int(last_printed_histories/self.plan_histories*100)
                Progress_bar(share).print_res()
                time.sleep(5)
            except FileNotFoundError:
                time.sleep(0.5)
                print("\rAwaiting for running code...", end="\r")
            except IndexError:
                print("\rAwaiting for running code...", end="\r")
                time.sleep(0.5)
            except Exception as e:
                print(e)
                time.sleep(10)
            
            for i in self.check_finished:
                for j in self.FINISHED:
                    if j in i:
                        Progress_bar(100).print_res()
                        print('\n')
                        run=False

        stdout, stderr = await proc.communicate()
        if stdout:
            print(f'[stdout]\n{stdout.decode()}')
        if stderr:
            print(f'[stderr]\n{stderr.decode()}')


    def prep_path(self, file, code="a"):
        dr = os.path.join(self.cwd, file)
        os.chdir(dr)
        self.plan_histories = self.get_histories
        burn_file_name = [i for i in os.listdir() if re.search(self.BURN, i)][0]
        self.cmd = f'{self.MCUMPI_BAT} > {self.LOG_FILE} f {burn_file_name} {code} {self.cores}'
        asyncio.run(self.async_loop())
        return
    
    def run(self):
        if not len(self.files)>0:
            return print("No files to run")
        with concurrent.futures.ProcessPoolExecutor() as executor:
            print(self.files)
            resulted = [executor.submit(self.prep_path, i) for i in self.files]
        # for f in concurrent.futures.as_completed(resulted):
        #     print(f.result)

class Clear(Handler):
    BURN:str = Run.BURN
    GEOM:str = r"\Ageom"
    MATR:str = r"\Amatr"
    MCU_BAT:str = Run.MCU_BAT
    MCUMPI_BAT:str = Run.MCUMPI_BAT

    def __init__(self, files:list, cores:int):
        super().__init__(files)
        self.cores=cores if cores==1 else round(cores/len(self.files))
        
    def clear(self):
        if not len(self.files)>0:
            return print("No files to delete")
        for i in self.files:
            dr = os.path.join(self.cwd, i)
            os.chdir(dr)
            burn_file_name = [i for i in os.listdir() if re.search(self.BURN, i)][0]
            os.system(f'{self.MCUMPI_BAT} f {burn_file_name} D {self.cores}')

class Progress_bar(Handler):
    LENGTH = 100

    def __init__(self, share):
        self.progress = share

    def print_res(self):
        progress_filled = Back.CYAN + self.progress*' ' + Back.RESET
        not_filled = (self.LENGTH-self.progress)*"."
        template = f"\r|{progress_filled}{not_filled}| {self.progress}%"
        print(template, end="\r")


class Extracter(Handler):
    def __init__(self):
        super().__init__(self)
