
from collections import defaultdict
import os
import re


class Filter:
    def __init__(self, paths, filter_mode, *keys):
        self.paths = paths
        self.filter_mode = filter_mode
        self.keys_how_tofilter = keys
        self.method = self.filter_method()
        
    # def __repr__(self):
    #     return

    @classmethod
    def single_path(cls, path):
        return cls([path])

    def loop_over_paths(self):
        for i in self.paths:
            yield i
        # return

    def get_dir_content(self, path):
        return os.listdir(path)

    #* loop over folder files
    def file_filter_bynames(self, string):
        for name in self.keys_how_tofilter:
            if name in string:
                return True
        return False

    def file_filter_byregex(self, string):
        for pattern in self.keys_how_tofilter:
            res = re.search(pattern, string)
            if res:
                return True
        return False

    def filter_method(self):
        match self.filter_mode:
            case "bynames":
                return getattr(self, "file_filter_bynames")
            case "byregex":
                return getattr(self, "file_filter_byregex")
            case _:
                raise AttributeError("No matches for given mode")

    #* returns list of filtered files
    def filter(self):
        filtered = defaultdict(list)
        for path in self.loop_over_paths():
            for file in self.get_dir_content(path):
                if self.method(file):
                    filtered[path].append(file)
                continue
        if not len(filtered) > 0:
            #*prevent errors on other interfaces due to empty dictionary
            raise IndexError("No folders left after filtering")  

        return filtered
                
