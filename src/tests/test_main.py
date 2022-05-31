import pytest
import os
from types import GeneratorType
from handler.main import Handler, Extracter

def test_check_folders():
    folders:list =  Handler().check_folders
    print(folders)
    assert 0

@pytest.fixture
def extracter_obj():
    test_data:str = "test_data/fin"
    path:str = os.path.join(os.path.split(os.path.dirname(__file__))[0], test_data)
    return Extracter(path, 'FIN', "500")

def test_find_files(extracter_obj):
    assert len(extracter_obj.files) == 0

def test_match_file(extracter_obj):
    assert len(extracter_obj.file) != 0

def test_read_file(extracter_obj):
    f = extracter_obj.read_file()
    print(type(f))
    assert type(f) == GeneratorType

    