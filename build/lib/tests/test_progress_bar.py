import pytest
from colorama import Back
from handler.progress_bar import Progress_bar


# class TestProgress_bar():
#     def __init__(self, share, current_step, steps, file, success=True):
#         self.progress = float(share/100)
#         self.progress_value = share
#         self.current_step = current_step
#         self.steps = steps
#         self.file = file
#         self.color=Back.CYAN if success else Back.RED

# @pytest.fixture
# def random_status():


@pytest.fixture
def prep_bars():
    bars_list:list = []
    for i in range(10):
        bars_list.append(Progress_bar(50+i*2, 1,1, "my_file", True).print_res)
    return bars_list

def test_bars(prep_bars):
    for i in prep_bars:
        i()
        # assert 0
    



# if __name__ == '__main__':
#     TestProgress_bar(50, 1,1, "my_file", False)
