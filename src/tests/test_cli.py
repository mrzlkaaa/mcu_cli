import pytest
import os
import re
import fire
from cli.CLI import CLI

PATH = lambda x: os.path.join(os.path.split(os.path.dirname(__file__))[0], x)

def test_run():
    CLI(mpi=20).run()
    assert 0

def test_extract():
    test_data:str = "test_data/fin"
    path = PATH(test_data)
    # path:str = os.path.join(os.path.split(os.path.dirname(__file__))[0], test_data)
    cli = CLI(filename="50")
    cli.extract(path=path, code="RATE", extension=".FIN")
    # print(cli.on_clear)
    assert 0

def test_filter():
    pattern = r"[^\\.].+[^\\]"
    folder_name1 = f"\\.test_2022.03.28_3-5_z\\"
    print(re.search(pattern, folder_name1).group())
    folder_name2 = "f2"
    CLI().run(folder_name1, folder_name2)

    assert 0