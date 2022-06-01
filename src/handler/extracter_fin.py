from .main import Extracter, Excel_exporter
from  collections import defaultdict
import numpy as np


class Fin(Extracter):
    KEFF:str = "Keff Briss"
    NEUT_HEAT:str = " Neutron heating, eV"
    PHOT_HEAT:str = " Photon heating, eV"
    PART_TYPE:str = "-- PARTICLE TYPE"
    FLUX:str = "FLUX."
    REACTRATE:str = "NUCLIDE:"

    def __init__(self, code:str, folder_path:str, extension:str, file_name:str=None):
        super().__init__(folder_path, extension, file_name)
        self.search_keyword = self.match_code(code.upper())
        self.particle_blocks = defaultdict(list)
        self.zone_blocks = defaultdict(list)
        # self.last_added_dd:str
        self.data_blocks = dict()
        # self.keyword = 
        return

    def match_code(self, code:str):
        match code:
            case "KEFF":
                return self.KEFF
            case "FLUX":
                return self.FLUX
            case "NHEAT":
                return self.NEUT_HEAT
            case "PHEAT":
                return self.PHOT_HEAT

    def particle_blocks_length(self, kys):
        return len(kys.keys())

    #! apply on for fluxes and reac_rates
    def define_datablocks(self): #TODO use threadPool to loop over files
        last_added_dd: str = ''
        val:int = 0
        switcher:bool = False
        for _, i in enumerate(self.file):
            self.data_blocks[i] = defaultdict(list)
            for nn, c in enumerate(self.read_file(i), start=1):
                if self.PART_TYPE in c:
                    # self.data_blocks[i][f"particle_block-{nn}"]
                    self.data_blocks[i][f"particle_block-{nn}"] = defaultdict(list)
                if self.search_keyword in c:
                    last_added_dd = list(self.data_blocks[i].keys())[len(self.data_blocks[i].keys())-1]
                    
                    self.data_blocks[i][last_added_dd]["NAMES"].append((nn, c.split()[-1]))
                    val = self.data_blocks[i][last_added_dd]["NAMES"][-1][0]
                    if isinstance(self.data_blocks[i][last_added_dd]["VALUES"], list):
                        self.data_blocks[i][last_added_dd]["VALUES"] = defaultdict(list)
                    switcher = not switcher
                elif val != 0 and nn-val >= 2 and switcher:
                    if len(c) < 3:
                        switcher = not switcher
                        continue
                    last_added_name = str(self.data_blocks[i][last_added_dd]['NAMES'][-1][-1])
                    self.data_blocks[i][last_added_dd]["VALUES"][str(last_added_name)] \
                        .append(np.array(c.strip().split(), dtype=np.float64))
                        
        # print(self.data_blocks)
    
    def data_formatting(self):
        inc:int = 0
        excel_export = Excel_exporter(file_name="test.xlsx")
        for file, file_data in self.data_blocks.items():
            excel_export.sheet = file
            for particle_block, particle_block_data in file_data.items():
                for particle_block_keys in particle_block_data["NAMES"]:
                    key = particle_block_keys[-1]
                    concentrated_arr = np.concatenate(particle_block_data["VALUES"][particle_block_keys[-1]])
                    row = int(concentrated_arr.size/3)
                    value_reshaped = np.reshape(concentrated_arr, (row, 3))
                    # print(value_reshaped)
                    excel_export.write(particle_block, key, value_reshaped)
        
        excel_export.wb.close()

                    


