import pytest
import os
import inspect
from types import GeneratorType
from handler.main import Handler, Extracter

wr_path = {'/mnt/c/Users/Nikita/Desktop/codes/mcu_code_runner/src/test_data/post_processing': ['124_burn.DAT']}

def test_check_folders():
    folders:list =  Handler().check_folders
    print(folders)
    assert 0

@pytest.fixture
def extracter_obj():
    test_data:str = "test_data/fin"
    path:str = os.path.join(os.path.split(os.path.dirname(__file__))[0], test_data)
    return Extracter(path, 'FIN')

def test_write():
    Handler(wr_path).write_file(
        '/mnt/c/Users/Nikita/Desktop/codes/mcu_code_runner/src/test_data/post_processing',
        '124_burn.DAT',

        "\
NAMV  fresh_heu_bur_axial \n\
MAXS  50 \n\
DTZM  1 \n\
FINISH  ï¿½ï¿½ï¿½ï¿½ï¿½ï¿½ï¿½ï¿½ï¿½ï¿½ ï¿½ï¿½ï¿½ï¿½ï¿½ ï¿½ï¿½ï¿½ï¿½ï¿½ï¿½ï¿½ \n\
*********************************** \n\
BURN \n\
CODE   RSTP \n\
FISZ   1 120 \n\
ABSZ   1250 1465 \n\
DPOW   7190 3.18, 0 10.9, 7190 3.18, 0 6.91, \n\
    7190 4.31, 0 6.56, 7190 3.09, 0 3.01, \n\
    7190 4.2, 0 2.87, 7190 4.21, 0 3.05, \n\
    7190 4.03, 0 2.85, 7190 4.19, 0 10.93, \n\
    7190 3.11, 0 10.66, 7190 3.78, 0 4.02, \n\
    7190 3.19, 0 65.54, \n\
DSTP   3.18 1, 10.9 1, 3.18 1, 6.91 1, \n\
    4.31 1, 6.56 1, 3.09 1, 3.01 1, \n\
    4.2 1, 2.87 1, 4.21 1, 3.05 1, \n\
    4.03 1, 2.85 1, 4.19 1, 10.93 1, \n\
    3.11 1, 10.66 1, 3.78 1, 4.02 1, \n\
    3.19 1, 65.54 1, \n\
COLI   1 \n\
ZONP   1 120, 1250 1465 \n\
SUMZ   SUMB ZONB \n\
CONT   DENS \n\
FINISH \n\
************************* \n\
RGS  1 1 \n\
PERC  0 \n\
NRET  4321 UP \n\
PTYPE  1 \n\
END \n\
FINISH ï¿½ï¿½ï¿½ï¿½ï¿½ï¿½ ï¿½ï¿½ï¿½ï¿½ï¿½ï¿½ï¿½ï¿½ï¿½ï¿½ï¿½\n"
        )
    assert 0

def test_find_files(extracter_obj):
    assert len(extracter_obj.files) == 0

def test_match_file(extracter_obj):
    assert len(extracter_obj.file) != 0

def test_read_file(extracter_obj):
    f = extracter_obj.read_file()
    print(type(f))
    assert type(f) == GeneratorType

def test_excel_exporter(extracter_obj):
    extracter_obj.excel_exporter()


    