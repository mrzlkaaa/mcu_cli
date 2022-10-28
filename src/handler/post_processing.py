from .main import Handler
import subprocess
import os


class Post_processing(Handler): #* should inherits from Run? 
    CODE = "CODE"
    def __init__(self, towork_with_files, pp_mode):
        super().__init__(towork_with_files)
        self._pp_mode = pp_mode.upper()

    @property
    def pp_mode(self):
        return self._pp_mode

    def DAT_edit_run(self):
        for folder, files in self.towork_with_files.items():
            os.chdir(folder)
            for file in files:
                content = []
                for i in self.read_file(folder, file):
                    content.append(i)
                    if self.CODE in i:
                        arr = i.split()
                        content[-1] = f"{arr[0]}   {self.pp_mode}\n"
                self.write_file(folder, file, content)
                self.run_command(file)

    def remove_extension(self, string):
        return string.split(".")[0]

    def run_command(self, file):
        file = self.remove_extension(file)
        cmd = f'{self.config["GENERAL"]["MCUMPI_BAT"]} f {file} b 1'
        print(f"running <{cmd}> in {os.getcwd()}")
        subprocess.run(cmd, shell=True)  #* actually algorithm should await for shell res
        return