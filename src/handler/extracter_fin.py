from .main import Extracter
from  collections import defaultdict


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
                # elif val != 0 and nn - val >= 2:
        return
    


