import pytest


from cli.runner.runs_chain import Chain
from cli.display.display import Display

@pytest.fixture
def chain():
    return Chain(
        folders_queued=[
            "f3", "f3_2", "f4", "f5"
        ],
        display=Display(),
        dev_path="/mnt/c/Users/Nikita/Desktop/codes/mcu_code_runner/src/cli/runner/test_data",
        cpu_number=2
    )

def test_distribute_runs(chain):
    chain._distribute_runs(
        cpu_number=3,
        folders_queued=[
            "f2", "f3", "f3_2", "f4", "f5", "f6", "f7"
        ]
    )
    assert 0