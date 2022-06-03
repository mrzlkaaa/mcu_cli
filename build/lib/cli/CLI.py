from . import load_options
from colorama import Fore
from handler.main import Handler
from handler.run import Run
from handler.extracter_fin import Fin
from handler.clear import Clear
import fire
import os


class CLI:
    bcolors = {
        "HEADER": Fore.MAGENTA,
        "OKGREEN" : Fore.GREEN,
        "OKCYAN" : Fore.CYAN,
        "WARNING" : Fore.YELLOW,
        "FAIL" : Fore.RED,
        "RESET" : Fore.RESET,
    }
    
    def __init__(self, filename=None, mpi=None): #todo move args to func?
        self.options = load_options()
        self.file_name = self.options["DEFAULT_NAME_PATTERN"] if filename is None else filename
        self.on_clear, self.on_run, \
            self.on_clear_str, self.on_run_str = self.status_formatter(Handler().check_folders)
        self.mpi = 1 if mpi is None else mpi

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
            return "NO avaliable files to handle"
        return f"{self.on_clear_str}\n{self.on_run_str}"

    # def line_length_formatter(self):

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
        Run(self.file_name, self.on_run, self.mpi).run()

    def extract(self, *key, **params):
        print(params)
        if len(key)>0:
            self.on_clear = self.filter(key, self.on_clear)
        for folder in  self.on_clear: #[params["path"]]:
            folder_path = os.path.join(os.getcwd(), folder)
            try:
                code, extension = params["code"], params["extension"]
                db = Fin(code, folder_path, extension, self.file_name)
                db.define_datablocks()
                db.excel_export()
            except KeyError:
                print("Code or extension is not given")
                # return
            

    def clear(self, *key):
        if len(key)>0:
            self.on_clear = self.filter(key, self.on_clear)
        Clear(self.file_name, self.on_clear, self.mpi).clear()
    
    def help(self):
        return "List of avaliable commands:\n\
        < status > - shows calculations status in folders of current directory\n\
        < clear arg1 arg2 ... > - initiates folders cleaning (removes files created by software run);\n\
        if arguments omitted will clear all folders\n\
        < run arg1 arg2 ... > - run calculations in folders of current directory;\n\
        if arguments omitted will run calculations in all folders\n"
       
def initiate():
    fire.Fire(CLI)

if __name__ == "__main__":
    initiate()


    