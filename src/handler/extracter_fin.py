from typing import final
from .main import Extracter
from .excel_exporter import Excel_exporter
from  collections import defaultdict
import numpy as np
import asyncio
import os
import re


class Fin(Extracter):
    KEFF:str = "Keff "
    NEUT_HEAT:str = " Neutron heating, eV"
    PHOT_HEAT:str = " Photon heating, eV"
    PART_TYPE:str = "-- PARTICLE TYPE"
    FLUX:str = "FLUX."
    REACTRATE:str = "REACTION:"

    def __init__(self, towork_with_files, code:str):
        super().__init__(towork_with_files, code)
        
        self.search_keyword, self.extract_method, \
             self.export_method = self.match_code()
        self.data_blocks = dict()

    def match_code(self):
        match self.code:
            case "KEFF":
                return self.KEFF, getattr(self, "keff_extraction"), getattr(self, "keff_excel_export")
            case "FLUX":
                return self.FLUX, getattr(self, "fr_extraction"), getattr(self, "fr_excel_export") 
            case "RATE":
                return self.REACTRATE, getattr(self, "fr_datablocks"), getattr(self, "fr_excel_export") 
            case "NHEAT":
                return self.NEUT_HEAT, 0
            case "PHEAT":
                return self.PHOT_HEAT, 0
            case "" | None:
                return None

    def excel_writer(self, name):
        return Excel_exporter(file_name=f"{name}.xlsx")

    async def run(self):
        background_tasks = []
        for path, files in self.towork_with_files.items():
            key_folder = os.path.split(path)[-1]
            self.data_blocks[key_folder] = defaultdict(list)
            background_task = asyncio.create_task(self.extract_method(path, key_folder, files))
            background_tasks.append(background_task)
        await asyncio.gather(*background_tasks)
        self.export_method()


    #* applied for keffs
    async def keff_extraction(self, path, key_folder, files):
        for file in files:
            self.data_blocks[key_folder][file] = defaultdict(list)
            self.data_blocks[key_folder][file]["0-th block"] = defaultdict(list)
            db_toblock_navigation = self.data_blocks[key_folder][file]["0-th block"]
            for _, lc in enumerate(self.read_file(path, file), start=0):
                if self.search_keyword in lc and not "(" in lc:
                    key_param_name = " ".join(lc.split()[:2])
                    values = np.array(lc.split()[-2:], dtype=np.float64)
                    db_toblock_navigation[key_param_name] = values


    def heats_extraction(self): #todo handler of heating data from .FIN
        return

    #* applied for fluxes and reac_rates
    async def fr_extraction(self, path, key_folder, files):
        switcher:bool = False
        for file in files:
            ln_keyword_detected: int = 0
            data_block_num:int = 0
            self.data_blocks[key_folder][file] = defaultdict(list)
            for ln, lc in enumerate(self.read_file(path, file), start=0):
                if self.PART_TYPE in lc:
                    data_block_num+=1
                    self.data_blocks[key_folder][file][f"{data_block_num}-th block"] = defaultdict(list)
                    db_toblock_navigation = self.data_blocks[key_folder][file][f"{data_block_num}-th block"]
                if self.search_keyword in lc:
                    obj_name = lc.split()[-1]
                    db_toblock_navigation[obj_name] = dict()
                    ln_keyword_detected = ln
                    switcher = not switcher
                elif ln -ln_keyword_detected >= 2 and switcher:
                    if not re.search(r"\S+", lc):
                        switcher = not switcher
                        continue
                    key_param_name = lc.split()[0]
                    values = np.array(lc.split()[-2:], dtype=np.float64)
                    db_toblock_navigation[obj_name][key_param_name] = values


    def fr_excel_export(self):
        for folder, files in self.data_blocks.items():
            excel_export = self.excel_writer(folder)
            print(folder)
            for file, blocks in files.items():
                excel_export.sheet = file
                row_shift:int = 0
                for name_block, data_block in blocks.items():
                    excel_export.write_header(name_block, 0) #* writes name of block at the top
                    for param_name, param_data in data_block.items():
                        excel_export.write_header(param_name, excel_export.position_row - 1) #* writes name of data at the top
                        for key, values in param_data.items():
                            excel_export.write_row([key, *values])
                            excel_export.position_row += 1
                        excel_export.position_row += 2
                    excel_export.position_row_reset()
                    excel_export.position_col += 5
                excel_export.position_col_reset()
            excel_export.wb.close()

    def keff_excel_export(self):
        for folder, files in self.data_blocks.items():
            excel_export = self.excel_writer(folder)
            print(folder)
            for file, blocks in files.items():
                excel_export.sheet = file
                for name_block, data_block in blocks.items():
                    excel_export.write_header(name_block, 0) #* writes name of block at the top
                    for key, values in data_block.items():
                        excel_export.write_row([key, *values])
                        excel_export.position_row += 1
                    excel_export.position_row_reset()
            excel_export.wb.close()

        






