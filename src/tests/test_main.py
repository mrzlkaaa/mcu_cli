import pytest
from handler.main import Handler

def test_check_folders():
    folders:list =  Handler().check_folders
    print(folders)
    assert 0