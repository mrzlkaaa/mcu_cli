from colorama import Fore
from Handlers import *
import fire




class CLI:
    OPTIONS = {
        1: "run all",
        2: "run specific file/files (type folder names with comma delimeter)",
        3: "clear all folders",
        4: "clear specific folders"
    }
    bcolors = {
        "HEADER": Fore.MAGENTA,
        "OKGREEN" : Fore.GREEN,
        "OKCYAN" : Fore.CYAN,
        "WARNING" : Fore.YELLOW,
        "FAIL" : Fore.RED,
        "RESET" : Fore.RESET,
    }
    
    def __init__(self, mpi=1):
        self.on_clear, self.on_run, \
            self.on_clear_str, self.on_run_str = self.status_formatter(Handler([]).check_folders)
        self.mpi = mpi

    def __repr__(self):
        return "use < mcu help > to see avaliable commands >"

    def embedding_color(self, string, type):
        return f"{self.bcolors[type]}{string}{self.bcolors['RESET']}"

    def intro_msg(self):
        msg = self.embedding_color('Gonna handle your mcu files? Choose option:\n', 'HEADER')
        for k,v in self.OPTIONS.items():
            msg+= f"\t{k} - {v}\n"
        return msg

    def status(self):
        if len(self.on_run) < 1:
            return f"{self.on_clear_str}"
        elif len(self.on_clear) < 1:
            return f"{self.on_run_str}"
        elif len(self.on_clear) < 1 and len(self.on_run) < 1:
            return "NO files avaliable for handle"
        return f"{self.on_clear_str}\n{self.on_run_str}"

    def status_formatter(self, status):
        ok:list = []
        progress: list = []
        bad: list = []
        ok_str:str = ""
        progress_str:str = ""
        bad_str:str = ""
        for k,v in status.items():
            folder = os.path.split(k)[-1]
            if len(v)==3:
                ok.append(folder)
            elif len(v)==2:
                progress.append(folder)
            else:
                bad.append(folder)
        ok_str = self.embedding_color(" ----> Finished\n".join(ok) + " ----> Finished", "OKGREEN")
        bad_str =  self.embedding_color(" ----> Not ran\n".join(bad) + " ----> Not ran", "FAIL")
        if len(progress) !=0:
            progress_str = self.embedding_color(" ----> Ran\n".join(progress) + " ----> Ran", "OKCYAN")
            ok = [*ok, *progress]
            print(ok)
            ok_str = ok_str + "\n" + progress_str
        return ok, bad, ok_str, bad_str

    def filter(self, key, files):
        return [i for i in files for j in key if i==j]

    def run(self, *key):
        if len(key)>0:
            self.on_run = self.filter(key, self.on_run)
        Run(self.on_run, self.mpi).run()

    def clear(self, *key):
        if len(key)>0:
            self.on_clear = self.filter(key, self.on_clear)
        Clear(self.on_clear, self.mpi).clear()
    
    def help(self):
        return "List of avaliable commands:\nstatus - shows status of folders in current directory\n\
        clear <arg1> <arg2> ... - initiate folders cleaning (remove files except burn, geom, matr)\n\
        run <arg1> <arg2> ... - run mcu files"
       
def initiate():
    fire.Fire(CLI)

if __name__ == "__main__":
    initiate()


    