import os
import re
import toml
from datetime import datetime


__all__ = [
    "clear",
    "write",
    "read",
    "read_toml",
    "dump_toml",
    "datetime_rename"
]

def clear(
    path:str
):
    extensions = [
        r".+.DAT",
        r".+.LST",
        r".+.MCU",
        r".+.PMC",
        r".+.SCR",
        r".+.SYS",
        r".+.RGS",
        r".+.RST",
        r".+.ini"
    ]
    pattern = "|".join(extensions)
    to_remove = []
    files = os.listdir(path)
    for i in files:
        # print(i)
        res = re.search(pattern, i)
        if res:
            os.remove(
                os.path.join(
                    path,
                    res.string
                )
            )
    
    return

def write(
    path:str,
    content:str | list
) -> None:
    
    #* writes multistep file in a folder
    with open(path, "w") as f:
        if isinstance(content, str):
            f.write(content)
            return
        f.writelines(content)
    return

def read(
    path:str,
    as_lines: bool = True
) -> list | str:
    with open(path, "r") as f:
        if as_lines:
            return f.readlines()
        return f.read()


def read_toml(
    path:str
):
    with open(path, "r") as f:
        return toml.load(f)

def dump_toml(
    path:str,
    obj: dict
):
    with open(path, "w") as f:
        toml.dump(obj, f)

def datetime_rename(
    path:str,
    rename_pattern:str,
    suffix:str | None = None
):
    #* handling with None
    try:
        suffix = "_" + suffix
    except TypeError:
        suffix = ""

    files = os.listdir(path)
    for i in files:
        res = re.search(rename_pattern, i)
        if res:
            now = datetime.now()
            now_str = f'_{now.strftime("%d-%m-%Y_%H-%M-%S")}'
            
            os.rename(
                os.path.join(
                    path,
                    res.string
                ),
                os.path.join(
                    path,
                    f"{res.string}{suffix}{now_str}"
                )
            )
            return
    raise FileNotFoundError(".FIN file was not found")