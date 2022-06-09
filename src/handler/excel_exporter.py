
import xlsxwriter
from collections import namedtuple 

class Excel_exporter():
    DEFAULT_CELL_SIZE = 8
    def __init__(self, **kwargs):
        self.wb = xlsxwriter.Workbook(kwargs.get("file_name"))
        self._sheet = None
        self._origin = self.origin
        self.position = {"row":1,"col":1}
        self._block_format = self.block_format
        self._values_format = self.values_format

    @property
    def block_format(self):
        return  self.wb.add_format({
            "bold": True,
            "border": 1})

    @property
    def values_format(self):
        return self.wb.add_format({
            "num_format":11
        })
                
    @property
    def sheet(self):
        return self._sheet
    
    @sheet.setter
    def sheet(self, sheet):
        self._sheet = self.wb.add_worksheet(sheet)
        
    @property
    def origin(self):
        Position = namedtuple("origin", ["row", "col"])
        return Position(1, 1)

    def cells_num(self, text):
        return round(len(text)/self.DEFAULT_CELL_SIZE)

    def cell_size(self, text):
        return round(self.DEFAULT_CELL_SIZE*len(text)/self.DEFAULT_CELL_SIZE)
        
    def write_block(self, block, shift):
        self.position["row"], self.position["col"] = 1, 1
        self.position["col"] += 5*shift
        self.sheet.write(self.position["row"], self.position["col"], block)
        self.position["row"]+=2

    def write_key(self, key):
        self.sheet.write(self.position["row"], self.position["col"], "M/Z/O/E")
        self.sheet.write(self.position["row"], self.position["col"]+1, key)
        self.position["row"]+=1
        return

    def write_val(self, values, shift:bool=False):
        for r, lvalue in enumerate(values, start=1):
            for c, value in enumerate(lvalue, start=1):
                self.sheet.write(self.position["row"] , self.position["col"]+c, value, self.values_format)
            self.position["row"]+=1
        if shift: self.position["row"]+=2

    def write_col(self, values):
        for n, value in enumerate(values):
            self.sheet.write(self.position["row"]+n, self.position["col"], value, self.values_format)

    def write_row(self):
        return