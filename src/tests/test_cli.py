import pytest
import os
import re
import fire
import asyncio
from cli.CLI import CLI
from handler.main import Handler

PATH = lambda x: os.path.join(os.path.split(os.path.dirname(__file__))[0], x)
test_data:str = "test_data/fin"
test_data_keff_fin = "test_data/keff"

# @pytest.mark.asyncio
def test_status():
    asyncio.run(CLI().status())
    # await CLI().status()
    assert 0

def test_extract_fin():
    asyncio.run(CLI().extract_fin(code="keff"))
    assert 0

def test_extract_rez():
    asyncio.run(CLI().extract_rez(code="selected"))
    assert 0

@pytest.mark.asyncio
async def test_run():
    # folder_name2 = f"f1"
    CLI(mpi=20).run()
    assert 0

@pytest.mark.asyncio
async def test_rerun():
    folder_name1 = f"\\.f1\\"
    folder_name2 = f"f1"
    CLI(mpi=20).restart(folder_name2)
    assert 0

def test_copy():
    asyncio.run(CLI().copy("f1"))
    # await CLI().status()
    assert 0


def test_regex_filter():
    pattern = r"[^\\.].*[^\\]"
    folder_name1 = f"\\.test_2022.03.28_3-5_z\\"
    folder_name2 = f"\\.f1\\"
    folder_name3 = "test_2022.03.28_3-5_z"
    print(re.search(pattern, folder_name1).group())
    print(re.search(pattern, folder_name2).group())
    print(re.search(pattern, folder_name3).group())
    assert 0

def test_status_formatter():
    cli = CLI().status
    assert 0
