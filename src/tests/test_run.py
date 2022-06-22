import pytest
import os
import time
from .test_progress_bar import bar_instance
from handler.run import Run

#* simulate log file
def log_data():
    file_name:str = "test_data/log/BNCT_Failed.txt"
    path:str = os.path.join(os.path.split(os.path.dirname(__file__))[0], file_name)
    with open(path) as f:
        for line in f:
            if "Histories" in line:
                val = line.split()[-1] 
                yield int(val)
            elif "job aborted" in line:
                yield "aborted"



@pytest.mark.usefixtures("bar_instance")
@pytest.mark.parametrize("histories", log_data())
def test_async_loop(histories, bar_instance):
    mx:int = 80000000
    if isinstance(histories, str):
        bar_instance.progress = 100
        bar_instance.success = False
        bar_instance.print_res()
    else:
        bar_instance.progress = histories/mx*100
        bar_instance.print_res()
        print("would like to restart?")
    assert mx == histories
    # folder: list = ["log"]
    # cores:int = 1

    # Run(file_name, folder, cores).async_loop()