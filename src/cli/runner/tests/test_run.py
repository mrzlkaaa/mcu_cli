from re import template
import pytest
import os
import time
from collections import deque

from cli.runner.run import Run
from cli.display.display import Display



@pytest.fixture
def run():
    return Run(
        display=Display(),
        dev_path="/mnt/c/Users/Nikita/Desktop/codes/mcu_code_runner/src/cli/runner/test_data",
        folders=[
            "f3", "f3_2", "f4", "f5"
        ], 
        cpu_number=2
    )

def test_check_avaliable_cores(run):
    
    assert run._check_avaliable_cores(cpu_number=2) == None

def test_runs_initialization(run):
    run._runs_initialization()
    assert 0



def test_multistep_initialization(run):
    multistep_config = {
        'multistep': 
        {
            'anyname': {
                "0": 
                {
                    'name': 'HCH1',
                    "st_value" : 1,
                    'step': 0.1, 
                    'num_steps': 5,
                    "root_file_name":"geom_be_tvs_6layer_20.09.2021",
                    "template": "RPP  N1   -25,120  -15,85   -50,HCH1",
                    'nested': {
                        'name': 'DCH', 'step': 0.5, 'num_steps': 1
                    }
                },
                "1": 
                {
                    'name': 'RCH',
                    "st_value" : 1.5,
                    'step': 0.2, 
                    'num_steps': 3,
                    "root_file_name":"geom_be_tvs_6layer_20.09.2021",
                    "template": "RCZ Nb2   60,54,54   H-50  RCH"
                    
                }
            }
        }
    }

    run._multistep_initialization(
        folder="f3",
        multistep_config=multistep_config['multistep']
    )
    assert 0

def test_make_multistep_content(run):
    res = run._make_multistep_content(
        template="RPP  N1   -25,120  -15,85   -50,HCH1",
        key_name="HCH1",
        st_value=1,
        step=0.1,
        num_steps=5
    )
    print(res)
    assert 0

def test_add_reference(run):
    run._add_reference(
        path="/mnt/c/Users/Nikita/Desktop/codes/mcu_code_runner/src/cli/runner/test_data/f3_2/geom_be_tvs_6layer_20.09.2021",
        search_key="anyname_1",
        replace_key="anyname_1_1"
    )    
    assert 0

def test_multistep_validity(run):
    
    res = run._multistep_validity(
        "f3_2"
    )
    print(res)
    assert 0

def test_execute_calculation(run):
    assert run._execute_calculation(run.folders[0]) == None

def test_read_log(run):
    file_path = os.path.join(
        os.path.split(
            os.path.dirname(__file__)
        )[0],
        "test_data",
        "read_log",
        "20.09.2022_burn_log.txt"   
    )
    res = run._read_log(
        file_path=file_path,
        stage="PROGRESS",
        fetch_series=True
    )
    assert type(res) == int

def test_calculation_process(run):
    # file_path = os.path.join(
    #     os.path.split(
    #         os.path.dirname(__file__)
    #     )[0],
    #     "test_data",
    #     "f5",
    #     "20.09.2021_burn_log.txt"   
    # )
    run.progress = Display().progress_bar()
    progress_id = run.progress.add_task(
        "f5",
        total=9
    )
    run._calculation_process(
        "f5",
        progress_id
    )
    assert 0

def test_execute(run):
    run.execute()
    assert 0

def test_rename_fin(run):
    run._rename_fin(
        path="/mnt/c/Users/Nikita/Desktop/codes/mcu_code_runner/src/cli/runner/test_data/f4",
        suffix="anyname_0_1"
    )
    assert 0

def test_clear(run):
    run.clear(
        path="/mnt/c/Users/Nikita/Desktop/codes/mcu_code_runner/src/cli/runner/test_data/f4"
    )
    assert 0

