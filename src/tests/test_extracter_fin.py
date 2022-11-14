import pytest
import os
import asyncio
from collections import defaultdict
from handler.extracter_fin import Fin
from .test_cli import PATH

dd_keff:defaultdict = {
        '/mnt/c/Users/Nikita/Desktop/codes/mcu_code_runner/src/test_data/f6': ['burn.FIN'],
        '/mnt/c/Users/Nikita/Desktop/codes/mcu_code_runner/src/test_data/f7': ['burn.FIN', 'burn.FIN_B0', 'burn.FIN_B1' ], 
        # '/mnt/c/Users/Nikita/Desktop/codes/mcu_code_runner/src/test_data/keff': ['123_burn.FIN_B0', '123_burn.FIN_B1', '123_burn.FIN_B10', '123_burn.FIN_B11', '123_burn.FIN_B12', '123_burn.FIN_B13', '123_burn.FIN_B14', '123_burn.FIN_B15', '123_burn.FIN_B16', '123_burn.FIN_B17', '123_burn.FIN_B18', '123_burn.FIN_B19', '123_burn.FIN_B2', '123_burn.FIN_B20', '123_burn.FIN_B21', '123_burn.FIN_B22', '123_burn.FIN_B23', '123_burn.FIN_B24', '123_burn.FIN_B25', '123_burn.FIN_B3', '123_burn.FIN_B4', '123_burn.FIN_B5', '123_burn.FIN_B6', '123_burn.FIN_B7', '123_burn.FIN_B8', '123_burn.FIN_B9']
        }

dd_fr:defaultdict = {
        '/mnt/c/Users/Nikita/Desktop/codes/mcu_code_runner/src/test_data/fin': ['5001_mini.FIN', 'BNCT_dis.FIN', 'BNCT_heat.FIN', 'BNCT_spec.FIN']
        }

dd_r:defaultdict = {
        '/mnt/c/Users/Nikita/Desktop/codes/mcu_code_runner/src/test_data/fin': ['5001_mini_rr.FIN']
        }

@pytest.fixture
def fin_keff():
    return Fin(dd_keff, "keff")

@pytest.fixture
def fin_f():
    return Fin(dd_fr, "flux")

@pytest.fixture
def fin_r():
    return Fin(dd_r, "rate")

def test_basics(fin_keff):
    print(fin_keff.toextract_files)
    print(fin_keff.search_keyword)
    assert 0

def test_match_code(fin_keff):
    f = fin_keff.search_keyword
    assert type(f) == str


@pytest.mark.asyncio
async def test_keff_data(fin_keff):
    await fin_keff.run()
    # fin_obj.excel_export()
    assert 0

@pytest.mark.asyncio
async def test_f_data(fin_f):
    await fin_f.run()
    assert 0

@pytest.mark.asyncio
async def test_r_data(fin_r):
    await fin_r.run()
    assert 0

    