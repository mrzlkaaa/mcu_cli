
from datetime import datetime
from distutils import extension
from typing import Iterable
# from ...handler.main import Handler
# from ...handler.progress_bar import Progress_bar
import os
import re
import random
import math

import subprocess
import concurrent.futures
import asyncio
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from threading import Thread, Lock

from collections import deque, defaultdict

from cli.display.display import Display
from cli.support import *
from cli.support.main import read_toml

lock = Lock()

class Run:
    '''
   #* This class in developed to run
   #* mcu code files
   #* Main idea is to simplify process of
   #* running, handling mcu input/output files
   #* Some main aspects of mcu code files:
   #*   - mcu code file can be splitted on multiply files
   #*     to increase readability / simplify debbuging
   #*     BUT there is ONE PARENT file useы as a main
   #*     to execute calculation
   #*   - calculation can be run in multithread mode
   #*   - mcu file is not default and can consist any of ASCII symbols
   #* This module provides functionality to
   #*   - check avaliabilty of cores to distibute them
   #*     between all folders choosen to run calculation
   #*   - make multi_step calculations by changing input files
   #*     (mcu provides multistep calculation only in BURNUP module
   #*     but in some cases the multistep mode without BURNUP can be
   #*     super useful.
   #*     EXAMPLE. The task is to get control rod worth over core height.
   #*     The number of run depends on how descrete results are required.
   #*     So let's assume we need 20 runs. That means that the only difference between
   #*     all these runs is in z-coordinate of rod/rods)
   #*     To ease such tasks i propose non-burnup multistep funtionality
   #*     which based on replacing part of code via #INCULDE tag
   #*     Actually whole process may be described like
   #*     Set number of steps -> Run -> After step is finished it renames .FIN to FIN_Sn
   #*     where n - is number of step -> clear temporary files -> Run
   #*     After all steps are finished we do have a set of FIN_Sn files 
   #* Attributes
   #* ----------
   #*
   #* Methods
   #* ----------
    '''
    #! this class variables better to be moved to a system configuration file
    MCU_BAT = "mcu5mpi.bat"
    ERROR = "job aborted"
    ERROR2 = "error:"
    RUN_STAGES = {          
            "INPUT": ["state calculation"], #* "MCU Step: state input",
            "PROGRESS": ["No burnup in the task (file *.sb not found)", "The task is finished."] #* "MCU Step: state calculation"       
    }
    CALC_CONFIG = "!calculation_config.toml"
    CHAIN_CONFIG = "!calculation_chain.toml"
    BACKUP_SUFFIX = "backup.toml"
    AUTO_RESTARTS_LIMIT = 10

    def __init__(
        self, 
        folders: Iterable, 
        display: object | None = None,
        cpu_number:int = 1,
        dev_path:str | None = None,
        restart:bool = False
    ) -> None:
        self.display = display
        self.cwd = os.getcwd() if not dev_path else dev_path #* for testing only
        self._check_avaliable_cores(len(folders)*cpu_number)
        self.cpu_number = cpu_number
        self.progress_data = dict()
        
        self.onrun = folders
        self.calculating = []
        self.finished = []
        self.failed = []
        
        self._runs_initialization(restart)

        

    
    def _check_avaliable_cores(
        self,
        cpu_number: int
    ) -> int:
        '''
        #* Check avaliable cores
        #* to use for run / runs
        #* If cpu_number > cores avaliable throw ValueError
        #* Parameters
        #* ----------
        #*  cpu_number: int
        #*      number of CPU to use
        #* Raises
        #* ----------
        #* ValueError
        #*  raises if cpu_number > cores avaliable
        #* Returns
        #* ----------
        #*
        '''
        try:
            #* For UNIX only
            avaliable_cores = len(os.sched_getaffinity(0))
        except AttributeError:
            avaliable_cores = os.cpu_count()
        
        if (avaliable_cores-cpu_number) < 0:
            raise ValueError(
                f"The number of avaliable CPU is {avaliable_cores}, but {cpu_number} required"
            )
        return
        

    def _add_reference(
        self,
        path: str,
        search_key: str,
        replace_key:str,
    ):
        '''
        #* Support method to replace reference name of file
        #* during multistep calculations to upload info
        #* stored in reference file 
        #* key search followed
        #* by replacement has implemented
        #* During iteration the step order changes only
        #* So to simply search method i proposed to search
        #* not for a full name of step file (anyname_0_0) to
        #* replace it by next file (anyname_0_1) but use
        #* current state name [ anyname_0 ]_0 that is in step file name
        #* Parameters
        #* ----------
        #*  path: str
        #*      path to open root file to make search and replacement
        #*  search_key: str
        #*  replace_key: str
        #* Raises
        #* ----------
        #*  None
        #* Returns
        #* ----------
        #*  None
        '''
        search_template = f"#INCLUDE {search_key}"
        replace_template = f"#INCLUDE {replace_key}\n"

        # print(path)
        with open(path, "r") as f:
            content = f.readlines()

            for n, i in enumerate(content):
                if search_template in i:
                    content[n] = replace_template
                    break
            
        #* if occurances not found 
        #* unchanged content writes 
        write(
            path,
            content
        )
        
        return
    

    def _make_multistep_content(
        self,
        template:str,
        key_name:str,
        st_value:float,
        step: float,
        num_steps:int
    ):
        '''
        #* Support method to create an array
        #* of multistep content
        #* key_name in template replaced by numerical
        #* value (float) recieved by incrementing
        #* of starting value by a change (step)
        #* multiplied by a step number
        #* First element in array is content with
        #* no increments so it's zero step
        #* Parameters
        #* ----------
        #*
        #* Raises
        #* ----------
        #*
        #* Returns
        #* ----------
        #*
        '''
        #* creates list of contexts
        queue = [
            template.replace(key_name, "{:.2f}".format(st_value+step*i)) 
            for i in range(num_steps)
        ]
        queue_indexes = [i for i in range(num_steps)]
        
        # print(queue)
        return queue, queue_indexes
    
    def _multistep_initialization(
        self,
        folder: str,
        root_file:str,
        multistep_config: dict
    ):
        '''
        #* Multistep implementaion
        #* It's main step for multistep calculations  
        #* At zero step (initialization)
        #* Parameters
        #* ----------
        #*
        #* Raises
        #* ----------
        #*
        #* Returns
        #* ----------
        #*
        '''
        # print(f"starting multistep init for {folder}")
        # print(multistep_config)
        multistep_progress = {}

        # multistep_progress["queues"] = defaultdict(list)
        #* unpacking multistep configurations
        #* and populating new dict
        files_queue = deque()
        for file, file_data in multistep_config.items():
            multistep_progress[file] = {}
            
            files_queue.append(file)
            

            states_queue = deque()
            for state, state_data in file_data.items():
                
                states_queue.append(state)
                #* keyword to search in file
                # multistep_progress[file]["current_step"] = 0
                multistep_block = f"{file}_{state}"
                
                multistep_progress[file][multistep_block] = {}
                multistep_progress[file][multistep_block]["name"] = state_data["name"]
                
                
                queue_contexts, queue_indexes = self._make_multistep_content(
                    state_data["template"],
                    state_data["name"],
                    state_data["st_value"],
                    state_data["step"],
                    state_data["num_steps"],
                )

                multistep_progress[file][multistep_block]["contents"] = queue_contexts
                multistep_progress[file][multistep_block]["queue"] = deque()
                # multistep_progress[file][multistep_block]["context_queue"]
                
                steps_queue = deque()
                # multistep_progress[file][multistep_block]["queue"].append(multistep_block)
                for i, step in enumerate(queue_contexts):
                    step_file_name = f"{multistep_block}_{str(i)}"
                    
                    steps_queue.append(step_file_name)
                    
                    multistep_progress[file][multistep_block]["queue"].append(step_file_name)
                    step_file_path = os.path.join(
                        self.cwd,
                        folder,
                        step_file_name
                    ) 

                    
                    write(
                        step_file_path,
                        queue_contexts[i]
                    )

                #* adds reference to file
                #* At this step first stp file has been added
                self._add_reference(
                     os.path.join(
                        self.cwd,
                        folder,
                        root_file,
                    ),
                    multistep_block,
                    multistep_progress[file][multistep_block]["queue"].popleft()
                )

        # print(multistep_progress)
        return multistep_progress

    def _runs_initialization(
        self,
        restart:bool
    ) -> None:
        '''
        #* Internal method to build and populate 
        #* dictionary by data required to
        #* run mcu calculation, build progress bar
        #* and make paths
        #* If case of multistep configurations
        #* makes multistep dictionary where
        #* calculation queue created. Creates multistep
        #* files with content to inserted to a main mcu file
        #* Method enables restart feature to continue calculation from
        #* a calculation step it has failed.
        #* restart feature required only for multistep calculations
        #* to prevent multistep data imports from overwritting
        #* (multistep data references were overwritten so calculations
        #* were started from a first step )
        #* Parameters
        #* ----------
        #*  restart: bool
        #*      enables backup file search
        #*      if found uploads data to self.progress_data   
        #* Raises
        #* ----------
        #*  None
        #* Returns
        #* ----------
        #*  None
        '''
        

        for i in self.onrun:
            self.progress_data[i] = dict()
            path_to_folder = os.path.join(
                self.cwd,
                i
            )

            #* if triggers the backup uploads
            #* and populates the progress_data
            #* In this case MCU code file does not modify
            #* to prevent overwriting
            if restart:
                path_to_backup = os.path.join(
                    path_to_folder,
                    f"{i}_{self.BACKUP_SUFFIX}"
                )
                #* if condition failed starts with default initialization
                if os.path.exists(path_to_backup):
                    folder_backups = read_toml(
                        path_to_backup
                    )
                    self.progress_data[i] = folder_backups
                    print("restarted", self.progress_data)
                    
                    #* moves to next i
                    continue
                

            path_to_config = os.path.join(
                path_to_folder,
                self.CALC_CONFIG
            )

            config_data = read_toml(
                path_to_config
            )
            
            self.progress_data[i]["folder_path"] = path_to_folder #* required to run mcu .exe
            self.progress_data[i]["file_name"] = config_data["meta"]["file_name"]
            self.progress_data[i]["log_file_name"] = f'{config_data["meta"]["file_name"]}_log.txt'
            self.progress_data[i]["progress_total"] = config_data["control"]["MAXS"]
            self.progress_data[i]["auto_restarts"] = 0
            
            
            #* check whether config has multistep feature enabled
            #todo second condition is more about config validation to make sure it is correctly filled
            if config_data["meta"].get("multistep") and config_data.get("multistep"):
                self.progress_data[i]["multistep_progress"] = self._multistep_initialization(
                    i,
                    config_data["meta"]["file_name"],
                    config_data["multistep"]) 
            
            # self.progress_data[i]["status"] = "ONRUN"
        # print(self.progress_data)        
        return
        
        
    #* decorator to keep wathcing for errors
    
    def _read_log(
        self,
        file_path:str,
        stage: str,
        fetch_series:bool
    ):
        '''
        #* Method developed to retrive data from log file
        #* log file appends by run output from mcu software
        #* There are 3 types of data in output we need to take care of
        #*  ERROR - mcu run failed due to error. So we do search error keyword
        #*  in log file.
        #*  STAGE keyword - means the successfull finish of run stage
        #*  It can be detecting PROGRESS (CALCULATION) stage keyword 
        #*  so INPUT stage finished
        #*  SERIES value - it's value of last successfully finished series
        #*  It's only for PROGRESS (CALCULATION) stage
        #* Parameters
        #* ----------
        #*  file_path: str
        #*      path of log file to read
        #*  stage: str
        #*      current stage of run. Used to get keywords
        #*      from self.RUN_STAGES to do search
        #*  fetch_series: bool
        #*      It's only for PROGRESS (CALCULATION) stage
        #*      Method search for last outputted series value
        #*      to return it 
        #* Raises
        #* ----------
        #*  None
        #* Returns
        #* ----------
        #*  True
        #*      if ERROR keyword found in log file
        #*  value type of string
        #*      it's number of series calculated by mcu
        #*      returns only if fetch_series were passed
        #*      to self._read_log function
        #*      int value is not used to avoid
        #*      wrong validation by conditions:
        #*          if series takes 0 or 1 condition
        #*          may validate it as False or True
        #*          so may be the reason of broken logic
        #*  None
        #*      Indicates successful end of loop
        #*      Possible outcome if stage keyword
        #*      detected in log file
        '''
        content = read(file_path, as_lines=True)
        
        error = {i for i in content if self.ERROR in i}
        if error:
            return "ERROR"

        keys = self.RUN_STAGES[stage]
        detected = {i for i in content for k in keys if k in i}

        #* stage keywords detected so calculation moved to next stage
        if len(detected) > 0:
            return True

        if fetch_series:
            try:
                series = [i for i in content if "Series:..............." in i][-1]
            except IndexError:
                #* raises when calculation started but block
                #* consisted series number has not appeared yet
                series = "0"

            value = re.search(r"\d+", series).group()
            return value
        
        return
            

    def _stage_loop(
        self,
        **kwargs
    ):
        '''
        #* Method implements finite loop designed to fetch data
        #* from log file. Loop required to monitor changes in log file
        #* Depends on result recieved from self._read_log method
        #* decides whether to break or continue loop
        #* There 3 different returns in method: False, int, None
        #* Parameters
        #* ----------
        #*  **kwargs: dict
        #*      key-value arguments to be passed to self._read_log
        #* Raises
        #* ----------
        #*  None
        #* Returns
        #* ----------
        #*  False
        #*      if ERROR keyword found in log file
        #*      It immediatly terminates the stage loop
        #*      and returns name of folder
        #*  value type of string
        #*      it's number of series calculated by mcu
        #*      returns only if fetch_series were passed
        #*      to self._read_log function
        #*  None
        #*      Indicates successful end of loop
        #*      Possible outcome if stage keyword
        #*      detected in log file
        '''
        finished = False
        while not finished:
            
            res = self._read_log(
                **kwargs
            )
            if res == True:
                #* exit loop
                finished = True
            elif res == "ERROR":
                return False
            #* it's for fetching series    
            elif isinstance(res, str):
                #* return int
                return res
            
        return None
    
    async def subprocess_shell(
        self, 
        cmd:str,
        fd: str,
        folder:str,
        log_file_path:str
    ):
        '''
        #* Serves only to run mcu code
        #* This method calls by a thread
        #* Thread awaites until shell command returns
        #* Async shell subrocess allows us to check whether
        #* execution failed by reading log file
        #* But anyway this method freezes till result from
        #* shell not reutrned
        #* Parameters
        #* ----------
        #*  cmd: str 
        #*      command to be executed / called in a shell
        #*  folder: str
        #*      folder where cmd calls
        #*  log_file_path: str
        #*      path to log file to read it
        #* Raises
        #* ----------
        #*  None
        #* Returns
        #* ----------
        #*  None
        '''
        with lock:
        
            os.chdir(fd)
            proc = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            os.chdir(self.cwd)

        await asyncio.sleep(5)
        
        #* Now lets get folders that were failed on INPUT stage
        #* The input stages fnished in 2 cases:
        #*  - calculation moved to calculation stage
        #*  - input stage failed
        input_stage = self._stage_loop(
            file_path=log_file_path, 
            stage="INPUT",
            fetch_series=False
        )

        if input_stage == False:
            print(f"Running in {folder} failed")
            with lock:
                del self.progress_data[folder]
                self.onrun.remove(folder)
                self.failed.append(folder)
                
        elif input_stage is None:
            with lock:
                self.onrun.remove(folder)
                self.calculating.append(folder)

        await proc.communicate()
        # print("process returned")
        
        return


    def _execute_calculation(
        self,
        folder: str,

    ):
        '''
        #* Method prepares promt command to call .exe
        #* to run mcu code
        #* This method calls by independent thread
        #* lock is used to safely apply os.chdir
        #* dir changes back after executable called 
        #* To successfully run mcu code the follows required:
        #*  call os.chdir(path) to change directory and
        #*  emit cmd command with positional arguments to execute
        #*  .exe file of mcu software
        #*  cmd must be like:
        #*      <mcu.bat> >> <log_file> < f > < file_name > < a > < cpu_number >
        #*      where,
        #*          mcu.bat - bat file that passes arguments to .exe
        #*          >> - means that mcu output writes to a file
        #*          log_file - file where mcu output writes
        #*          f - name of calculational module of mcu
        #*          file_name - name of main mcu code file 
        #*          a - is type of calculation
        #*          cpu_number - number of cpu to use for calculation 
        #* After cmd prepared method call self.subprocess_shell to call
        #* mcu executable
        #*
        #*  
        #* Parameters
        #* ----------
        #*  folder: str
        #*      Name of folder where mcu exeutable will be called
        #* Raises
        #* ----------
        #*  None
        #* Returns
        #* ----------
        #* None | str
        '''
        #* folder destination
        fd = self.progress_data[folder]["folder_path"]
        log_file_path = os.path.join(
            fd,
            self.progress_data[folder]["log_file_name"]
        )

        #!!! >> for tests only
        cmd = f'{self.MCU_BAT} > {self.progress_data[folder]["log_file_name"]} f {self.progress_data[folder]["file_name"]} a {self.cpu_number}'
        # print(f"starting calculation by command: {cmd} in folder {os.getcwd()}\n")
        
        asyncio.run(
            self.subprocess_shell(
                cmd,
                fd,
                folder,
                log_file_path
            )
        )

        return


    #! NO DOCS
    def _multistep_validity(
        self,
        folder:str
    ):
        '''
        #* Internal metrhod that is created to validate
        #* that there is a next step in multistep calculation in
        #* a given folder
        #* validation process based on check a queue
        #* if queue is not empty and does returns the name of 
        #* next step file it means that multistep process has not finished yet
        #* method makes a backup to make a checkpoint of calculation process
        #* and returns data to let next method finish multistep preparations
        #* Parameters
        #* ----------
        #*  folder: str
        #*     string to iterate over self.progress_data and
        #*     retrieve required data
        #* Raises
        #* ----------
        #* None
        #* Returns
        #* ----------
        #*  file: str
        #*     name of file that is under multistep calculation
        #*  state: str
        #*      current state of multistep for a current file
        #*  next_step: str
        #*      name of file that will be used as reference
        #*      for a next calculation step
        #*  None
        #*      In case of multistep data not found or
        #*      multistep process has finished -> all queue are empty
        '''
        folder_data = self.progress_data[folder]
        if folder_data.get("multistep_progress"):
            #* iterating over multistep files
            for file, file_data in folder_data["multistep_progress"].items():
                #* iterating over multistep states
                for state, state_data in file_data.items():
                    try:
                        #* get queue value to consume
                        #! when works with backup file
                        #! deque transormed to list< so popleft failed
                        #! create new exception where make list to deque back!
                        if isinstance(state_data["queue"], list):
                            state_data["queue"] = deque(state_data["queue"])
                        next_step = state_data["queue"].popleft()
                        #* makes backup before consume
                        path_to_backup = os.path.join(
                            self.cwd,
                            folder,
                            f"{folder}_{self.BACKUP_SUFFIX}"
                        )
                        dump_toml(
                            path_to_backup,
                            folder_data
                        )
                        return file, state, next_step
                    except IndexError:
                        #* exception thows if queue is empty 
                        #* and nothing left to pop
                        #* So moves to the next state
                        #todo drop state safely
                        continue
        return
    

    #! NO DOCS
    def _multistep_change(
        self,
        folder:str
    ):
        '''
        #* Top method to make multistep calculation
        #* It does call self._multistep_validity to
        #* validate multistep process
        #* If validation successfull it does:
        #*  make changes in mcu file -  (replace reference name)
        #*  clear folder (remove mcu data to enable run)
        #*  rename .FIN file to prevent it from overwrittinng
        #* Parameters
        #* ----------
        #*  folder: str
        #*     name a folde where to validate multistep
        #*     make changes, clear folder and rename .FIN 
        #* Raises
        #* ----------
        #*  None
        #* Returns
        #* ----------
        #*  True
        #*      True indicates that folder is
        #*      prepared for another cmd call
        #*      (actually status of folder is
        #*       now "Avaliable to run")
        #*  None
        #*      Multistep data not found
        '''
        validity = self._multistep_validity(folder)
        if not validity:
            return None
        
        file, state, step = validity
        self._add_reference(
            os.path.join(
                self.cwd,
                folder,
                self.progress_data[folder]["file_name"]
            ),
            state,
            step
        )
        #todo merge clear and rename in one method
        clear(
            path=os.path.join(
                self.cwd,
                folder
            )
        )

        fin_pattern = r".+.FIN\Z"
        datetime_rename(
            path=os.path.join(
                self.cwd,
                folder
            ),
            rename_pattern=fin_pattern,
            suffix=file
        )
        return True

    async def _calculation_process(
        self,
        folder:str,
        # progress_id
    ):
        '''
        #* Internal method called by gatherer in self.call
        #* It watches for progress during calculation
        #* stage in a given folder and display it
        #* ProgressBar is used to display calculation progress
        #* ProgressBar updates in while loop using
        #* results returned by self._stage_loop
        #* ProgressBar changes progress value in case of 
        #* self._stage_loop returns int value that is higher than conuter value
        #* (conuter is local variable used to check if returned series value changed)
        #* <From self._stage_loop there 3 different types of returning data>
        #* If res == Failed returned by self._stage_loop:
        #*  The ProgressBar updates as "ABORTED"
        #* if res is value type of int and res > conuter:
        #*  The ProgressBar completed value changes to res value
        #* If res is None:
        #*  The ProgressBar updates to FINISHED
        #* Parameters
        #* ----------
        #*  folder: str
        #*      Name of folder to monitor calculation progress
        #*      Also used to build a path to log file
        #*      and retrive data from self.progress_data
        #*  progress_id
        #*      Used to update specific progress of ProgressBar
        #* Raises
        #* ----------
        #*  None
        #* Returns
        #* ----------
        #*  There are 3 positional returns here:
        #*      folder_name: str | None
        #*          
        '''
        
        #* This loop freezes this method for a some time
        #* It's made to let self.subprocess_shell safely
        #* pass input stage. If self.subprocess_shell failed
        #* method finishes
        while True:
            # print("DO check if folder executed")
            
            #* exit loop
            #* and popup the progress bar
            #* for progress displaying
            if folder in self.calculating:
                # print(f"MONITORING of {folder} started")
                break
            #* exit function by returning None
            #* so coro finishes 
            elif folder in self.failed:
                # print(f"EXIT FOR {folder}")
                return (None, None, None)

        await asyncio.sleep(10)
        
        progress_id = self.progress.add_task(
            description=folder,
            total=self.progress_data[folder]["progress_total"],
            start=True
        )
        # print(f"Creates {progress_id}")
        log_file_path = os.path.join(
            self.progress_data[folder]["folder_path"],
            self.progress_data[folder]["log_file_name"]
        )
        
        counter = 0
        while True:
            await asyncio.sleep(1)

            res = self._stage_loop(
                file_path=log_file_path,
                stage="PROGRESS",
                fetch_series=True
            )
            if  res is None:
                self.progress.update(
                    progress_id, 
                    completed=self.progress_data[folder]["progress_total"],
                    description=f"FINISHED {folder}"
                )
                
                #* finish of loop
                return (1, folder, progress_id)
            elif res == False:
                
                self.progress.update(
                    progress_id, 
                    description=f"ABORTED {folder}"
                )
                self.progress.stop_task(progress_id)

                #* error
                return (0, folder, progress_id)
            elif isinstance(res, str):
                series = int(res)
                if series > counter:
                    self.progress.update(progress_id, completed=series)
                    counter = series
        

    #! Move docs to self.call method
    def execute(self):
        '''
        #* Execute mcu run in every folder
        #* Run progress writes to log file with a name of file_name_log.txt
        #* log file append every time stage changes / series finished.
        #* This method developed to call execution command in promt,
        #* check log files and conclide which files were run / failed
        #* It is method just to run calcs in different threads
        #* ThreadPoolExecutor is used to execute each run asynchronously
        #* Each thread is responsible to call execution command
        #* No monitoring feathres at this step due to thread in locked at process
        #* If running failed stdout throws
        #* After process finished final stdout displays
        #* Parameters
        #* ----------
        #* None
        #* Raises
        #* ----------
        #* None
        #* Returns
        #* ----------
        #* None
        '''
        print(f"Execution of < {', '.join(self.onrun)} > has started")
        # st = time.time()
        with ThreadPoolExecutor(max_workers=len(self.onrun)) as executor:
            # for folder, _ in self.progress_data.items():
            futures_exec = [executor.submit(self._execute_calculation, folder) for folder in self.progress_data.keys()]  

        return 
        

    async def call(self):
        '''
        #* Top method to initiate calculation
        #* Here all folders start calculation
        #* one by one. 
        #* In each folder gatherer is used to
        #* call a thread and process concurrently
        #* because of thread is freezes due to shell command execution
        #* but self._calculation_process let us watch
        #* for progress in this folder
        #* There is while loop here which is used to await
        #* for all asyncio task finished
        #* It's running unill all tasks finished
        #* But in case when multistep enabled
        #* awatables tasks appends so loop cannot be finished
        #* Tasks appends by self._multistep_change
        #* If it does return True
        #* Parameters
        #* ----------
        #* None
        #* Raises
        #* ----------
        #*
        #* Returns
        #* ----------
        #*
        '''

        #* this initialization required after awaitable 
        #* returns result -> folder name

        #* it's execution block
        self.progress = self.display.progress_bar()
        with self.progress:

            aws = []
            for folder in self.onrun:
                #* awaitables
                aws.append(
                    asyncio.gather(
                        asyncio.to_thread(self._execute_calculation, folder),
                        self._calculation_process(folder)
                    )   
                )
            
            #* getting results and 
            #* enter to finite multistep loop
            to_add = []
            while not len(aws) == 0:
                await asyncio.sleep(5)
                #* getting results from awaitables
                for aw in asyncio.as_completed(aws):
                    _, (calc_status, folder, progress_id) = await aw
                    await asyncio.sleep(5)

                    # print(f"retrieved res {folder}")
                    #* calc is finished
                    if folder and calc_status:
                            multistep = self._multistep_change(folder)
                            if multistep:
                                to_add.append(folder)
                                self.progress.remove_task(progress_id)
                                #* multistep data was found
                                #* use lock to safely classify folder as onrun
                                with lock:
                                    # print("Next step has prepared for ", folder)
                                    self.onrun.append(folder)
                                    self.calculating.remove(folder)
                                continue
                            #* multistep data was not found
                            #* use lock to safely classify folder as finished
                            with lock:
                                self.calculating.remove(folder)
                                self.finished.append(folder)
                            
                    
                    #* calc is aborted due to mcu error
                    elif folder and not calc_status:
                        
                        if self.progress_data[folder]["auto_restarts"] > self.AUTO_RESTARTS_LIMIT:
                            #* number of times the calculation was restarted has exceeded limit
                            #* use lock to safely classify folder as failed
                            with lock:
                                self.calculating.remove(folder)
                                self.failed.append(folder)
                            continue
                    
                        to_add.append(folder)
                        self.progress.remove_task(progress_id)
                        #* increments the number of restarts
                        self.progress_data[folder]["auto_restarts"] += 1

                        #* use lock to safely classify folder as onrun
                        with lock:
                                self.calculating.remove(folder)
                                self.onrun.append(folder)
                        print(
                            f"calc in {folder} is about to restart\n",
                            "number of restarts made:",
                            self.progress_data[folder]["auto_restarts"]
                        )
                        
                    # print(f"No multistep files for {folder}")
                aws.clear()
                
                #! do not like
                if len(to_add) > 0:
                    for f in to_add:
                        aws.append(
                            asyncio.gather(
                                asyncio.to_thread(self._execute_calculation, f),
                                self._calculation_process(f)
                            )
                        )
                    await asyncio.sleep(2)
                    to_add.clear()
            # print("extit calculation loop")
                
            return
        
    @classmethod
    def call_chain(
        cls,
        folders_chain: list,
        display: object | None,
        cpu_number: int,
        cpu_max:int | None = None,
        with_restart: bool = True
    ):
        '''
        #* Run calculations in chain-like style
        #* Accepts finite number of folders
        #* and split them on bunches
        #* the size of bunch depends on
        #* max cpu on PC and how much CPU required
        #* for a single folder calculation
        #* Therefore, 
        #*  if 4 folders with 4 CPU required are given (16 in total)
        #*  but only 8 CPUs avaliable on PC, method computates
        #*  the number of runs that can be run concurrently (8 // 4 = 2)
        #*  and create a bunches with 2 foldres in each bunch
        #*  Finally, total number of runs gets as follows:
        #*  number of given folders / number of concurrent runs
        #*  Float results ceils to 2 ( 4 / 2 = 2)
        #*  So for a given example we need to call Run.call() method
        #*  2 times (2 folder calculates concurrently) to get all 4 folders
        #*  finished
        #* Described implementation let us create a queues of calculation
        #* which will be run one by one synchronously.
        #* By classmethod decorator we do call Run().call() 
        #* as an independant instances
        #* Parameters
        #* ----------
        #*  folders_chain: list
        #*      folders that are prepared to be run
        #*  display: object
        #*      Display class to dispalay progress bars
        #*  cpu_number: int
        #*      Number of CPU required for a single folder calculation
        #*  with_restart: bool
        #*      Passes to Run method to make restarts 
        #*      (if backup file exists) in calculation folder
        #* Raises
        #* ----------
        #*  ValueError
        #*      raises if cpu_number > max cores on PC
        #* Returns
        #* ----------
        #*  None
        '''

        chain_config_path = os.path.join(
            os.getcwd(),
            cls.CHAIN_CONFIG
        )

        if not os.path.exists(chain_config_path):

            if cpu_max is None or cpu_max > os.cpu_count():
                cpu_max = os.cpu_count()
            
            #* check if cpu_number < cpu_max
            if cpu_max < cpu_number:
                raise ValueError(
                    f"The number of CPU is {cpu_max}, but {cpu_number} were given"
                )

            #* gets number of parallel runs 
            #* takes integer only
            concurrent_runs = cpu_max // cpu_number
            
            total_runs = math.ceil(len(folders_chain) / concurrent_runs)
            

            progress_chain = dict()
            progress_chain["meta"] = {}
            progress_chain["meta"]["cpu_number"] = cpu_number

            progress_chain["chain"] = {}
            #* so now folders_queued splits on total_runs parts
            for n, i in enumerate(range(0, total_runs)):
                progress_chain["chain"][str(n)] = folders_chain[
                    i*concurrent_runs:concurrent_runs+i*concurrent_runs
                ]

            
            dump_toml(
                chain_config_path,
                progress_chain
            )

        else:
            progress_chain = read_toml(
                chain_config_path
            )

        for folders in progress_chain["chain"].values():
            run = cls(
                folders=folders,
                display=display,
                cpu_number=cpu_number,
                restart=with_restart
            )
            print(
                f"starts with {folders}"
            )
            asyncio.run(run.call())
            
        

   