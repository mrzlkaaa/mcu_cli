from .main import Handler
from .progress_bar import Progress_bar
import os
import re
import time
import concurrent.futures
import subprocess
import asyncio

class Run(Handler):
    def __init__(self, file_name, towork_with_files:list, cores:int):
        super().__init__(towork_with_files)
        self.file_name = file_name
        self.folder:str
        self.cores = cores if cores==1 else self.cores_distribution(cores)
        self.plan_histories:int = 1
        self.calculation_steps: list = [1]
        self.detected_burnup_lines:set = set()

    def cores_distribution(self, cores):
        print(cores)
        try:
            cores:int = round(cores/len(self.towork_with_files))
            return cores
        except ZeroDivisionError:
            print("No files to run")
        except Exception as e:
            raise e

    def read_file(self, file):
        with open(file) as f:
            con = f.readlines()
        return con

    def check_calc(self, context):
        for k, v in self.config["RUN"]["CALC_STATUS"].items():
            for vv in v:
                for n, i in enumerate(context):
                    if vv in i and k == "OK":
                        return False, k, vv
                    elif vv in i and k == "ERROR":
                        return False, k, vv
                    elif vv in i and k == "BURNUP" and not n in self.detected_burnup_lines:
                        self.detected_burnup_lines.add(n)
                        return True, k, ""
        return True, "", ""

    def check_log_exists(self):
        log_path = os.path.join(os.getcwd(), self.LOG_FILE)
        file_exists = os.path.exists(log_path)
        if file_exists:
            os.remove(log_path)
        

    @property            
    def input_analyzing(self):
        # history:int
        file_name = [i for i in os.listdir() if re.search(fr"{self.file_name}\Z", i)][0]
        self.LOG_FILE = file_name + ".txt"
        context = self.read_file(file_name)
        self.calculation_steps = [*self.calculation_steps, *[i.split(",")[-1] for i in context for j in self.config["RUN"]["FC_CONFIG"] if j in i]]
        history_coefs = [i.split()[-1] for i in context for j in self.config["RUN"]["RUN_CONFIG"] if j in i]
        for i in history_coefs:
            self.plan_histories *= int(i)
        return file_name

    #! requered significant revision (move while loop to Progress Bar interface
    #! to make the Progress Bar idea use clear and reusable)
    async def async_loop(self):
        self.check_log_exists()
        proc = await asyncio.create_subprocess_shell(
            self.cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE)

        run:bool = True
        share:int = 0
        last_printed_histories:int
        current_step:int = 1
        success:bool = True
        bar = Progress_bar(share, current_step, len(self.calculation_steps), self.folder)
        while run==True:
            try:
                context = self.read_file(self.LOG_FILE) #todo what if file already exists
                run, status, msg = self.check_calc(context)
                if len(msg) == 0:
                    printed_histories = [int(i.split()[-1]) for i in context if self.config["RUN"]["HISTORIES"] in i]
                    last_printed_histories = printed_histories[-1]
                    share = int(last_printed_histories/self.plan_histories*100)
                    if status == "BURNUP":
                        current_step+=1
                        bar.current_step = current_step
                    bar.progress = share
                    bar.print_res()
                    # Progress_bar(share, current_step, len(self.calculation_steps), self.file).print_res() #! create instance only once and only update variable
                    time.sleep(5)
                    continue
                # else:
                    # success:bool = False
                if status == "ERROR":
                    success = not success
                    bar.success = success
                bar.progress = 100
                bar.print_res()
                print(f"\n{msg}")
                    # Progress_bar(100, current_step, len(self.calculation_steps), self.file, success).print_res()
                
            except FileNotFoundError:
                print("\rAwaiting for running code...", end="\r")
                time.sleep(0.5)
            except IndexError:
                print("\rAwaiting for running code...", end="\r")
                time.sleep(0.5)
            except Exception as e:
                print(e)
                time.sleep(10)
            except KeyboardInterrupt:
                subprocess.run("Y")

        stdout, stderr = await proc.communicate()
        if stdout:
            print(f'[stdout]\n{stdout.decode()}')
        if stderr:
            print(f'[stderr]\n{stderr.decode()}')


    def prep_path(self, folder_path, code=None):
        if code is None:
            code = "a"
        os.chdir(folder_path)
        self.folder = os.path.split(folder_path)[-1]
        file_name = self.input_analyzing
        self.cmd = f'{self.config["GENERAL"]["MCUMPI_BAT"]} >> {self.LOG_FILE} f {file_name} {code} {self.cores}' #* >> to append file (in case run restarting)
        asyncio.run(self.async_loop())
        return
    
    def run(self):
        
        if not len(self.towork_with_files)>0:
            return print("No files to run")
        with concurrent.futures.ProcessPoolExecutor() as executor:
            resulted = [executor.submit(self.prep_path, i) for i in self.towork_with_files] 
        # iterate over all submitted tasks and get results as they are available
        for future in resulted:
            # get the result for the next completed task
            try:
                result = future.result()
            except UnicodeDecodeError:
                print("can't display result")