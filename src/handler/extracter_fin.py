from typing import final
from .main import Extracter
from .excel_exporter import Excel_exporter
from  collections import defaultdict
import numpy as np


class Fin(Extracter):
    KEFF:str = "Keff "
    NEUT_HEAT:str = " Neutron heating, eV"
    PHOT_HEAT:str = " Photon heating, eV"
    PART_TYPE:str = "-- PARTICLE TYPE"
    FLUX:str = "FLUX."
    REACTRATE:str = "REACTION:"

    def __init__(self, code:str, folder_path:str, extension:str, file_name:str=None):
        super().__init__(folder_path, extension, file_name)
        self.code = code.upper()
        self.search_keyword, self.extract_method, \
             self.split_index = self.match_code()
        # self.last_added_dd:str
        self.data_blocks = dict()
        self.extract_method()
        # self.keyword = 
        return

    def match_code(self):
        match self.code:
            case "KEFF":
                return self.KEFF, getattr(self, "keff_data"), np.arange(-2,1)
            case "FLUX":
                return self.FLUX, getattr(self, "fr_datablocks"), -1
            case "RATE":
                return self.REACTRATE, getattr(self, "fr_datablocks"), 1
            case "NHEAT":
                return self.NEUT_HEAT, 0
            case "PHEAT":
                return self.PHOT_HEAT, 0
            case "" | None:
                return None

    @property
    def excel_writer(self):
        return Excel_exporter(file_name=f"{self.folder_path.split()[-1]}_{self.code}.xlsx")
    # def extract(self):
    #     self.extract_method()


    def get_last_added_db(self, i):
        print(self.data_blocks[i].keys())
        return list(self.data_blocks[i].keys())[len(self.data_blocks[i].keys())-1]

    def keff_data(self):
        for _, i in enumerate(self.file):
            self.data_blocks[i] = defaultdict(list)
            self.data_blocks[i][f"{i}"] = defaultdict(list)
            for nn, c in enumerate(self.read_file(i), start=1):
                if self.search_keyword in c:
                    last_added_db = self.get_last_added_db(i)
                    splitted = c.split()
                    # print(nn, splitted[-2:])
                    self.data_blocks[i][last_added_db]["NAMES"] \
                        .append(f"{splitted[0]} {splitted[1]}")
                    if isinstance(self.data_blocks[i][last_added_db]["VALUES"], list):
                        self.data_blocks[i][last_added_db]["VALUES"] = defaultdict(list)
                    self.data_blocks[i][last_added_db]["VALUES"][f"{splitted[0]} {splitted[1]}"] \
                        .append(np.array(splitted[-2:], dtype=np.float64))
        return self.data_blocks

    # def print_keff_data(self):



    def heat_data_blocks(self):
        return

    #! applied for fluxes and reac_rates
    def fr_datablocks(self): #TODO use threadPool to loop over files
        last_added_db: str = ''
        val:int = 0
        switcher:bool = False
        for _, i in enumerate(self.file):
            self.data_blocks[i] = defaultdict(list)
            for nn, c in enumerate(self.read_file(i), start=1):
                if self.PART_TYPE in c:
                    # self.data_blocks[i][f"particle_block-{nn}"]
                    self.data_blocks[i][f"particle_block-{nn}"] = defaultdict(list)
                if self.search_keyword in c:
                    last_added_db = self.get_last_added_db(i)  #list(self.data_blocks[i].keys())[len(self.data_blocks[i].keys())-1]
                    
                    self.data_blocks[i][last_added_db]["NAMES"] \
                        .append((nn, c.split()[self.split_index]))
                    val = self.data_blocks[i][last_added_db]["NAMES"][-1][0]
                    if isinstance(self.data_blocks[i][last_added_db]["VALUES"], list):
                        self.data_blocks[i][last_added_db]["VALUES"] = defaultdict(list)
                    switcher = not switcher
                elif val != 0 and nn-val >= 2 and switcher:
                    if len(c) < 3:
                        switcher = not switcher
                        continue
                    last_added_name = str(self.data_blocks[i][last_added_db]['NAMES'][-1][-1])
                    self.data_blocks[i][last_added_db]["VALUES"][last_added_name] \
                        .append(np.array(c.strip().split(), dtype=np.float64))
                        
        return self.fr_excel_export()


    def fr_excel_export(self):
        excel_export = self.excel_writer
        for file, file_data in self.data_blocks.items():
            shift_col:int = 0
            excel_export.sheet = file
            for particle_block, particle_block_data in file_data.items():
                excel_export.write_block(particle_block, shift_col)
                shift_col+=1
                for particle_block_keys in particle_block_data["NAMES"]:
                    key = particle_block_keys[-1] if isinstance(particle_block_keys, tuple) else particle_block_keys
                    concentrated_arr = np.concatenate(particle_block_data["VALUES"][key])
                    try:
                        row = int(concentrated_arr.size/3)
                        values_reshaped = np.reshape(concentrated_arr, (row, 3))
                    except ValueError:
                        row = int(concentrated_arr.size/2)
                        values_reshaped = np.reshape(concentrated_arr, (row, 2))
                    
                    excel_export.write_key(key)
                    excel_export.write_val(values_reshaped, True)
        
        excel_export.wb.close()

    def keff_excel_export(self):
        excel_export = self.excel_writer
        excel_export.sheet = "Keff"
        print(self.data_blocks.keys())
        shift_col:int = 0
        for file, file_data in self.data_blocks.items():
            excel_export.write_block(file, shift_col)
            shift_col+=1
            for block, block_data in file_data.items():
                excel_export.write_col(block_data["NAMES"])
                for block_keys in block_data["NAMES"]:
                    values = block_data["VALUES"][block_keys]
                    excel_export.write_val(values)

        excel_export.wb.close()






