import pytest
import os
import asyncio
from handler.info import Info, MCU


@pytest.fixture
def test_info():
    info = Info()
    return info

@pytest.fixture
def test_mcu_info():
    info = MCU()
    return info


def test_get_dirs_files(test_info):
    print(test_info.dir_list)
    print(test_info.files_list)
    print(test_info.paths_todirs)
    
    assert 0

def test_mcu_folder_check(test_mcu_info):
    asyncio.run(test_mcu_info.calc_status())
    print(test_mcu_info.onrun)
    print(test_mcu_info.inprogress)
    print(test_mcu_info.finished)
    assert 0
