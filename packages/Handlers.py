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
    LOG_FILE:str

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
    BURN_FC = ("STEP", "DSTP")
    BURN_config = {
         "NTOT",
         "NBAT",
         "MAXS"
    }
    HISTORIES = "Histories"
    CALC_STATUS = { "OK":       {"The task is finished.",
                                 "No burnup in the task (file *.sb not found)"},
                    "ERROR":    {"job aborted"},
                    "BURNUP":   {"MCU Step: burnup"}}

    def __init__(self, files:list, cores:int):
        super().__init__(files)
        self.file:str
        self.cores=cores if cores==1 else round(cores/len(self.files))
        self.plan_histories:int = 1
        self.calculation_steps: list = [1]
        self.detected_burnup_lines:set = set()

    
    def read_file(self, file):
        with open(file) as f:
            con = f.readlines()
        return con

    def check_calc(self, context):
        for k, v in self.CALC_STATUS.items():
            for vv in v:
                for n, i in enumerate(context):
                    if vv in i and k != "BURNUP":
                        return False, k, vv
                    elif vv in i and k == "BURNUP" and not n in self.detected_burnup_lines:
                        self.detected_burnup_lines.add(n)
                        return True, k, ""
        return True, "", ""

    @property            
    def input_analyzing(self):
        # history:int
        file_name = [i for i in os.listdir() if re.search(self.BURN, i)][0]
        self.LOG_FILE = file_name + ".txt"
        context = self.read_file(file_name)
        self.calculation_steps = [*self.calculation_steps, *[i.split(",")[-1] for i in context for j in self.BURN_FC if j in i]]
        history_coefs = [i.split()[-1] for i in context for j in self.BURN_config if j in i]
        for i in history_coefs:
            self.plan_histories *= int(i)
        return file_name


    async def async_loop(self):
        proc = await asyncio.create_subprocess_shell(
        self.cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)

        run:bool = True
        last_printed_histories:int
        current_step:int = 1
        # print("Progress Bar is below")
        while run==True:
            try:
                context = self.read_file(self.LOG_FILE)
                run, status, msg = self.check_calc(context)
                if len(msg) == 0:
                    printed_histories = [int(i.split()[-1]) for i in context if self.HISTORIES in i]
                    last_printed_histories = printed_histories[-1]
                    share = int(last_printed_histories/self.plan_histories*100)
                    if status == "BURNUP":
                        current_step+=1
                    Progress_bar(share, current_step, len(self.calculation_steps), self.file).print_res()
                    time.sleep(5)
                else:
                    success:bool
                    if status == "OK":
                        success=True
                    else:
                        success=False
                    Progress_bar(100, current_step, len(self.calculation_steps), self.file, success).print_res()
                    print(f"\n{msg}")
            except FileNotFoundError:
                print("\rAwaiting for running code...", end="\r")
                time.sleep(0.5)
            except IndexError:
                print("\rAwaiting for running code...", end="\r")
                time.sleep(0.5)
            except Exception as e:
                print(e)
                time.sleep(10)

        stdout, stderr = await proc.communicate()
        if stdout:
            print(f'[stdout]\n{stdout.decode()}')
        if stderr:
            print(f'[stderr]\n{stderr.decode()}')


    def prep_path(self, file, code="a"):
        self.file = file
        dr = os.path.join(self.cwd, self.file)
        os.chdir(dr)
        burn_file_name = self.input_analyzing
        self.cmd = f'{self.MCUMPI_BAT} > {self.LOG_FILE} f {burn_file_name} {code} {self.cores}'
        asyncio.run(self.async_loop())
        return
    
    def run(self):
        if not len(self.files)>0:
            return print("No files to run")
        with concurrent.futures.ProcessPoolExecutor() as executor:
            print(self.files)
            resulted = [executor.submit(self.prep_path, i) for i in self.files]

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
    LENGTH:float = 70.0

    def __init__(self, share, current_step, steps, file, success=True):
        self.progress = float(share/100)
        self.current_step = current_step
        self.steps = steps
        self.file = file
        self.color=Back.CYAN if success else Back.RED

    def print_res(self):
        progress_filled = self.color + int(self.progress*self.LENGTH)*' ' + Back.RESET
        not_filled = int(self.LENGTH-int(self.progress*self.LENGTH))*"."
        template = f"\r|{progress_filled}{not_filled}| {self.progress*100}% | {self.current_step}/{self.steps} - ./{self.file}"
        print(template, end="\r")

class Extracter(Handler):
    def __init__(self):
        super().__init__(self)

class FIN_file(Extracter):
    def __init__(self):
        return

class REZ_file(Extracter):
    def __init__(self):
        return
