from .info import MCU
from collections import defaultdict
import re
import os
import shutil

class Copy():
    COPY_FOLDER_NAME = "COPIES"
    def __init__(self, paths, extensions_tocopy):
        self.paths = paths
        self.extensions = extensions_tocopy

    @staticmethod
    def folders_to_paths(folders):
        cwd = os.getcwd()
        print(cwd)
        return [os.path.join(cwd,i) for i in folders]

    @classmethod
    def single_extension(cls, paths, extension):
        return cls(paths, [extension])

    def input_files_regex(self, string, *patterns):
        for pattern in patterns:
            res = re.search(pattern, string)
            if res:
                return True
        return False

    def extension_regex(self, extension, string):
        pattern = re.compile(fr"{extension}\Z|{extension}_B\d+")
        match = pattern.search(string)
        if match is not None:
            return True
        return False

    def filter_files(self, path):
        filtered_files:list = []
        for i in os.listdir(path):
            if self.input_files_regex(i, r"\d+\.\d+\.\d+_\w+$", r"\d+_\w+$") or not "." in i:  #* patterns to match XX.XX.XX_TEXT and XX_TEXT
                print(i)
                filtered_files.append(i)
            for j in self.extensions:
                if self.extension_regex(j, i):
                    filtered_files.append(i)
        return filtered_files

    def populate_dict(self):
        filtered:dict = defaultdict(list)
        for i in self.paths:
            for j in self.filter_files(i):
                filtered[i].append(j)
        print(filtered)
        return filtered

    def create_folder(self, path):
        try:
            os.mkdir(path)
        except FileExistsError:
            raise FileExistsError(f"Fodler <{os.path.split(path)[-1]}> already exists")
        except FileNotFoundError as e:
            raise e

    def copy(self):
        print(self.extensions)
        copies_dst = os.path.join(os.getcwd(), self.COPY_FOLDER_NAME)
        self.create_folder(copies_dst)

        tocopy:dict = self.populate_dict() #todo async call and await till finished
        for k,v in tocopy.items():
            folder = os.path.split(k)[-1]
            dst_folder = os.path.join(copies_dst, "!" + folder)
            self.create_folder(dst_folder)
            for file in v:
                source = os.path.join(k,file)
                dst = os.path.join(dst_folder, file)
                shutil.copy2(source, dst)

        return
