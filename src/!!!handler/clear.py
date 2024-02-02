from .main import Handler
import os
import re

class Clear(Handler):
    # BURN:str = Run.BURN
    GEOM:str = r"\Ageom"
    MATR:str = r"\Amatr"
    # MCU_BAT:str = Run.MCU_BAT
    # MCUMPI_BAT:str = Run.MCUMPI_BAT

    def __init__(self, file_name, towork_with_files:list, cores:int):
        super().__init__(towork_with_files)
        self.file_name = file_name
        self.cores=cores if cores==1 else round(cores/len(self.files))
        
    def clear(self):
        if not len(self.towork_with_files)>0:
            return print("No files to delete")
        for i in self.towork_with_files:
            # dr = os.path.join(self.cwd, i)
            os.chdir(i)
            # file_name = [i for i in os.listdir() if re.search(fr"{self.file_name}\Z", i)][0]
            os.system(f'{self.config["GENERAL"]["MCUMPI_BAT"]} f {self.file_name} D {self.cores}')