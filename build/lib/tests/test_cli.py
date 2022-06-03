import pytest
import os
import fire
from cli.CLI import CLI



def test_extract():
    test_data:str = "test_data/fin"
    path:str = os.path.join(os.path.split(os.path.dirname(__file__))[0], test_data)
    cli = CLI(filename="50")
    cli.extract(path=path, code="RATE", extension=".FIN")
    # print(cli.on_clear)
    assert 0