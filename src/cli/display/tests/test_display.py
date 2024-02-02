import pytest
from cli.display.display import Display

d = {
    'info':  
        {
            '.pytest_cache': ['.gitignore', 'CACHEDIR.TAG', 'README.md', 'v'],
            'tests': ['test_info.py', '__init__.py', '__pycache__'], 
            '__pycache__': ['info.cpython-310.pyc', '__init__.cpython-310.pyc']
        }
}

rows = [
    ('f1', 'Finished / InProgress', 'danger'), 
    ('f2', 'Avaliable to run', 'good'), 
    ('f3', 'Avaliable to run', 'good'), 
    ('f4', 'Avaliable to run', 'good'), 
    ('f5', 'Avaliable to run', 'good'), 
    ('f6', 'Finished / InProgress', 'danger'), 
    ('f7', 'Finished / InProgress', 'danger')
]

@pytest.fixture
def display():
    return Display()

def test_tree(display):
    display.tree(d)
    assert 0

def test_table(display):
    display.table(
        cols=[
            "Folder", 
            "Status"
        ],
        rows_data=rows,
        title="Folders status",
    )
    assert 0

def test_progress_bar(display):
    display.progress_bar()

def test_status(display):
    display.status(
        status_text = "Calculation running...",
        finished_text = "Calculation started successfully",
        sleep_time = 2
    )
    assert 0