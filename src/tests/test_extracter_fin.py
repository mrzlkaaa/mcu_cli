import pytest
import os
from handler.extracter_fin import Fin
from .test_cli import PATH


test_data_fin:str = "test_data/fin"
test_data_keff_fin = "test_data/keff"

@pytest.fixture
def fin_obj():
    
    path:str = PATH(test_data_fin)
    test_code:str = "flux"
    return Fin(test_code, path, ".FIN", "dis")

@pytest.fixture
def tests_file_path():
    test_data:str = "test_data/fin"
    path:str = os.path.join(os.path.split(os.path.dirname(__file__))[0], test_data)
    return path

def test_match_code(fin_obj):
    f = fin_obj.search_keyword
    assert type(f) == str


def test_fr_datablocks(tests_file_path):
    fin_obj = Fin("flux", tests_file_path, "FIN", "dis")
    func_str = fin_obj.fr_datablocks.__name__
    get_func = getattr(fin_obj, func_str)
    dd = get_func()
    fin_obj.fr_excel_export()
    assert len(dd) < 0

def test_keff_data():
    path = PATH(test_data_keff_fin)
    fin_obj = Fin("keff", path, "FIN")
    func_str = fin_obj.fr_datablocks.__name__
    method_name = fin_obj.extract_method
    fin_obj.keff_data()
    # fin_obj()
    # fin_obj.excel_export()
    assert 0

# def test_excel_export(test_define_datablocks):
#     test_define_datablocks.excel_export()
    