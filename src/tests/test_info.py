import pytest
import os
import asyncio
from handler.info import Info, MCU


@pytest.fixture
def info_obj():
    info = Info()
    return info

@pytest.fixture
def mcu_obj():
    info = MCU()
    return info


def test_get_dirs_files(info_obj):
    print(info_obj.dir_list)
    print(info_obj.files_list)
    print(info_obj.paths_todirs)
    
    assert 0

def test_mcu_folder_check(mcu_obj):
    asyncio.run(mcu_obj.calc_status())
    print(mcu_obj.onrun)
    print(mcu_obj.inprogress)
    print(mcu_obj.finished)
    assert 0

def test_dir_list_property(info_obj):
    info_obj.dir_list = ["f1", "log"]
    print(info_obj.dir_list)
    print(info_obj.paths_todirs)
    assert 0

def test_check_isinprogress(mcu_obj):
    file = "5001_mini"
    mcu_obj.check_isinprogress(file)
    file = "5001_mini.ini"
    mcu_obj.check_isinprogress(file)
    assert 0
