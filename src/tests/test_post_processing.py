import re
import pytest
from handler.post_processing import Post_processing

dd = {
        '/mnt/c/Users/Nikita/Desktop/codes/mcu_code_runner/src/test_data/post_processing': ['124_burn.DAT'],
        '/mnt/c/Users/Nikita/Desktop/codes/mcu_code_runner/src/test_data/f6': ['20.09.2021_burn.DAT']
    }

@pytest.fixture
def pp_obj():
    return Post_processing(dd, "RFTB")

def test_dat_edit_run(pp_obj):
    pp_obj.DAT_edit_run()
    assert 0
