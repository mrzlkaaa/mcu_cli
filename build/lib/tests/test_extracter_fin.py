import pytest
import os
from handler.extracter_fin import Fin

@pytest.fixture
def fin_obj():
    test_data:str = "test_data/fin"
    path:str = os.path.join(os.path.split(os.path.dirname(__file__))[0], test_data)
    test_code:str = "RATE"
    return Fin(test_code, path, ".FIN", "50")

def test_match_code(fin_obj):
    f = fin_obj.search_keyword
    # files = fin_obj.files
    # #* do simple data print
    # fin_obj.data_formatting()
    assert type(f) == str
    return fin_obj


def test_define_datablocks(fin_obj):
    dd = fin_obj.define_datablocks()
    fin_obj.excel_export()
    assert len(dd) < 0


# def test_excel_export(test_define_datablocks):
#     test_define_datablocks.excel_export()
    