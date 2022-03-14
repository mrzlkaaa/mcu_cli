import os
import re
import concurrent.futures
import subprocess

class Handler:
    INI = r"\w+\.ini"
    FIN = r"\.FIN"

    def __init__(self, files:list):
        self.cwd = os.getcwd()
        self.files = files
        # self.structure = self.check_status

    # def loop(self):
    #     for root, dirs, files in os.walk("."):

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

    def __init__(self, files:list, cores:int):
        super().__init__(files)
        self.cores=cores if cores==1 else round(cores/len(self.files))
        print(self.cores)
        print(self.cwd)

    def prep_path(self, file):
        dr = os.path.join(self.cwd, file)
        os.chdir(dr)
        burn_file_name = [i for i in os.listdir() if re.search(self.BURN, i)][0]
        cmd = f'{self.MCUMPI_BAT} f {burn_file_name} a {self.cores}'
        print(dr)
        print(cmd)
        os.system(cmd)
        return
    
    def run(self):
        if not len(self.files)>0:
            return print("No files to run")
        with concurrent.futures.ProcessPoolExecutor() as executor:
            print(self.files)
            resulted = [executor.submit(self.prep_path, i) for i in self.files]
        for f in concurrent.futures.as_completed(resulted):
            print(f.result)

class Clear(Handler):
    BURN:str = Run.BURN
    GEOM:str = r"\Ageom"
    MATR:str = r"\Amatr"
    MCU_BAT:str = Run.MCU_BAT
    MCUMPI_BAT:str = Run.MCUMPI_BAT

    def __init__(self, files:list):
        super().__init__(files)

    def check_files(self, dir_files):
        current_dir = os.getcwd()
        for i in dir_files:
            if re.search(self.BURN, i) or re.search(self.GEOM, i) \
                or re.search(self.MATR, i) or re.search(self.MCU_BAT, i) or re.search(self.MCUMPI_BAT, i):
                continue
            os.remove(os.path.join(current_dir, i))
        
    def clear(self):
        if not len(self.files)>0:
            return print("No files to delete")
        for i in self.files:
            dr = os.path.join(self.cwd, i)
            os.chdir(dr)
            self.check_files(os.listdir())

class Extracter(Handler):
    def __init__(self):
        super().__init__(self)
