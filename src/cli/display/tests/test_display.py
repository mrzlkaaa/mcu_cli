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
    ('f1', "Not Finished"), 
    ('f2', "Not Finished"), 
    ('f3', "Not Finished"), 
    ('f4', "Not Finished"), 
    ('f5', "Not Finished"), 
    ('f6', "Finished"), 
    ('f7', "Finished")
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
        rows=rows,
        title="Folders status",
    )
    assert 0