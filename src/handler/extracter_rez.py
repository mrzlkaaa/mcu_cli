from .main import Extracter


class REZ(Extracter):
    MATERIAL_NUM = lambda x: f"Material     {x}" 
    SELECTED_ND:str = "SELECTED ISOTOPES. NUCLEAR DENSITY"
    ALL_ND:str = "FULL ISOTOPE LIST. NUCLEAR DENSITY"
    # def __init__(self):

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
        