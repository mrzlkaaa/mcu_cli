
import xlsxwriter
from collections import namedtuple 

class Excel_exporter():
    DEFAULT_CELL_SIZE = 8
    def __init__(self, **kwargs):
        self.wb = xlsxwriter.Workbook(kwargs.get("file_name"))
        self._sheet = None
        self._position_row = 2
        self._position_col = 1
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
    def position_row(self):
        return self._position_row

    @position_row.setter
    def position_row(self, val):
        self._position_row = val

    @property
    def position_col(self):
        return self._position_col

    @position_col.setter
    def position_col(self, val):
        self._position_col = val

    def position_row_reset(self):
        self.position_row = 2

    def position_col_reset(self):
        self.position_col = 1

    @property
    def shift_col(self):
        return self._shift_col

    @shift_col.setter
    def shift_col(self, val):
        self._shift_col = val


    def cells_num(self, text):
        return round(len(text)/self.DEFAULT_CELL_SIZE)

    def cell_size(self, text):
        return round(self.DEFAULT_CELL_SIZE*len(text)/self.DEFAULT_CELL_SIZE)


    #! make a shift an instance variable 
    def write_header(self, text, row):
        self.sheet.write(row, self.position_col, text)

    # #todo give an example what data_block template is
    # def write_data_block(self, data_block):
    #     self.position["row"], self.position["col"] = 2, 1
    #     # print(self.position["col"])
    #     self.position["col"] += 5*self.shift_col
    #     # self.position["row"] += 5*self.shift_row
    #     for k, block_values in data_block.items():
    #         self.sheet.write(self.position["row"], self.position["col"], k)
    #         self.write_col(block_values)
    #         self.position["row"]+=1

    # def write_key(self, key): #! not revised
    #     self.sheet.write(self.position["row"], self.position["col"], "M/Z/O/E")
    #     self.sheet.write(self.position["row"], self.position["col"]+1, key)
    #     self.position["row"]+=1
    #     return

    # def write_col(self, values):
    #     for n, value in enumerate(values, start=1):
    #         self.sheet.write(self.position["row"], self.position["col"]+n, value, self.values_format)

    def write_row(self, row:list):
        self.sheet.write_row(self.position_row, self.position_col, row)