import pytest
from handler.filter import Filter

paths = [
    "/mnt/c/Users/Nikita/Desktop/codes/mcu_code_runner/src/test_data/f1",
    "/mnt/c/Users/Nikita/Desktop/codes/mcu_code_runner/src/test_data/f3",
    "/mnt/c/Users/Nikita/Desktop/codes/mcu_code_runner/src/test_data/f5",
    "/mnt/c/Users/Nikita/Desktop/codes/mcu_code_runner/src/test_data/f6",
    "/mnt/c/Users/Nikita/Desktop/codes/mcu_code_runner/src/test_data/f7",
    "/mnt/c/Users/Nikita/Desktop/codes/mcu_code_runner/src/test_data/keff"
    ]
extensions = [".FIN", ".PDC", ".txt"]
toregex_strings = ["geom_be_tvs_6layer_20.09.2021", "burn.FIN", "burn.txt", "123_burn.FIN_B4", "burn.PDC"]


@pytest.fixture
def filter_bynames_inst():
    return Filter(paths, "bynames", "burn")

@pytest.fixture
def filter_byregex_inst():
    patterns = [fr"{extension}\Z|{extension}_B\d+" for extension in extensions]
    return Filter(paths, 
                "byregex", 
                r"\d+\.\d+\.\d+_\w+$",
                r"\d+\.\d+\.\d+\Z", 
                r"\d+_\w+$",
                r"\w+(_|-)\d+\Z",
                *patterns
                )

def test_file_filter_bynames(filter_bynames_inst):
    filtered = filter_bynames_inst.filter()
    print(filtered)
    assert 0

def test_file_filter_byregex(filter_byregex_inst):
    filtered = filter_byregex_inst.filter()
    print(filtered)
    assert 0
