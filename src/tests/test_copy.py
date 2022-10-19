import pytest
from handler.copy import Copy

folders = ["f1", "f2", "f5", "keff", "f8"]
extensions = [".FIN", ".PDC", ".txt"]
toregex_strings = ["geom_be_tvs_6layer_20.09.2021", "burn.FIN", "burn.txt", "123_burn.FIN_B4", "burn.PDC"]

def test_folders_to_paths(folders):
    paths = Copy.folders_to_paths(folders)
    return paths

@pytest.fixture    
def copy():
    paths = test_folders_to_paths(folders)
    return Copy(paths, extensions)

def test_extension_regex(copy):
    for i in toregex_strings:
        for j in extensions:
            copy.extension_regex(j, i)
    assert 0
    
def test_copy(copy):
    copy.copy()
    assert 0
    
