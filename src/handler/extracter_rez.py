from .main import Extracter
from collections import defaultdict
import os
import asyncio
import re



class Rez(Extracter):
    MATERIAL_NUM = lambda num: f"Material     {num}"  #* num is a number of MAT
    # MATERIAL_BURNUP = "{num} {type}. Burnup in Time"  #* num is a number of MAT, type stands for A (absorption) and F (fission)
    BURNUP = "Burnup in Time"
    SELECTED_ND:str = "SELECTED ISOTOPES. NUCLEAR DENSITY"
    FULL_ND:str = "FULL ISOTOPE LIST. NUCLEAR DENSITY"
    ALL_ND:str = " NUCLEAR DENSITY"

    def __init__(self, towork_with_files, code):
        super().__init__(towork_with_files, code)
        self.search_keyword = self.match_code()
        self.extract_method = self.data_extraction
        self.export_method = self.data_excel_export

    def match_code(self):
        match self.code:
            case "SELECTED":
                return self.SELECTED_ND
            case "FULL":
                return self.FULL_ND
            case "ALL":
                return self.ALL_ND
            case "BURNUP":
                return self.BURNUP
            
    async def data_extraction(self, path, key_folder, files):
        switcher:bool = False
        for file in files:
            ln_keyword_detected: int = 0
            self.data_blocks[key_folder][file] = defaultdict(list)
            self.data_blocks[key_folder][file]["0-th block"] = defaultdict(list)
            db_toblock_navigation = self.data_blocks[key_folder][file]["0-th block"]
            for ln, lc in enumerate(self.read_file(path, file), start=0):
                if self.search_keyword in lc and not "(" in lc:
                    obj_name = " ".join(lc.split()[:5])
                    db_toblock_navigation[f"{obj_name}"] = dict()
                    ln_keyword_detected = ln
                    switcher = not switcher
                elif ln - ln_keyword_detected > 1 and switcher:
                    if not re.search(r"\S+", lc) or re.search(r"#", lc):
                        switcher = not switcher
                        continue
                    #todo for row (array) consist of time steps needs to remove "d" character
                    key_param_name = lc[:9].strip()
                    values = lc[9:].split()
                    if key_param_name == "Time":
                        values = list(filter(lambda x: x != "d", values))  #* removes "d" character from array
                    values = self.convert_arr_to_float(values) #* convert it just before added to dd    
                    db_toblock_navigation[f"{obj_name}"][key_param_name] = values

    def data_excel_export(self):
        for folder, files in self.data_blocks.items():
            excel_export = self.excel_writer(folder)
            for file, blocks in files.items():
                excel_export.sheet = file
                for name_block, data_block in blocks.items():
                    excel_export.write_header(name_block, 0)  #* writes name of block at the top
                    for param_name, param_data in data_block.items():
                        excel_export.write_header(param_name, excel_export.position_row - 1)  #* writes name of data at the top
                        for key, values in param_data.items():
                            excel_export.write_row([key, *values])
                            excel_export.position_row += 1
                        excel_export.position_row += 2
                    excel_export.position_row_reset()
            excel_export.wb.close()