import pytest
import os
import pathlib
import asyncio
from cli.info.info import Info


@pytest.fixture
def info_obj():
    info = Info()
    return info

def test_dirs(info_obj):
    print(info_obj.folder_dirs)
    
    assert 0

def test_get_folders_status(info_obj):
    res = info_obj.get_folders_status()
    print(res)
    assert 0

def test_make_tree(info_obj):
    tree = info_obj._make_tree()
    print(tree)
    assert 0


def test_check_torun_folder(info_obj):
    test_data = os.path.join(
        os.path.split(
            os.path.dirname(__file__)
        )[0],
        "test_data",
        "f1"
    )
    folder = pathlib.Path(test_data)
    info_obj._check_torun_folder(folder)
    assert 0
    