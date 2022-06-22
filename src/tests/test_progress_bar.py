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


# def random_status():
@pytest.fixture
def bar_instance():
    bar = Progress_bar(0, 1,1, "my_file", True)
    return bar


@pytest.mark.parametrize("i", range(10))
def test_bar(i, bar_instance):
    print(bar_instance.progress)
    bar_instance.progress =  i*2
    bar_instance.print_res()
    assert 0
    



# if __name__ == '__main__':
#     TestProgress_bar(50, 1,1, "my_file", False)
