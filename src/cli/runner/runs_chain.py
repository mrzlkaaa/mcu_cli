from distutils.command.build_scripts import first_line_re
import os
import math
from collections import deque


from cli.runner.run import Run


class Chain:
    def __init__(
        self,
        folders_queued: list,
        cpu_number:int = 1,
        display: object | None = None,
        restart:bool = False
    ):
        
        
        # super().__init__(
        #     folders=[],
        #     display=display,
        #     cpu_number=cpu_number,
        #     dev_path=dev_path,
        #     restart=restart
        # )
        return

    def _distribute_runs(
        self,
        cpu_number: int,
        folders_queued: list
    ):
        max_cores = os.cpu_count()
        if max_cores < cpu_number:
            raise ValueError(
                f"The number of CPU is {max_cores}, but {cpu_number} were given"
            )

        total_cpu_required = cpu_number * len(folders_queued)

        #* gets number of parallel runs 
        #* takes integer only
        concurrent_runs = max_cores // cpu_number
        print(concurrent_runs)
        
        total_runs = math.ceil(len(folders_queued) / concurrent_runs)
        print(total_runs)

        progress_chain = dict()
        progress_chain["meta"] = {}
        progress_chain["meta"]["cpu_number"] = cpu_number

        progress_chain["chain"] = {}
        #* so now folders_queued splits on total_runs parts
        for n, i in enumerate(range(0, total_runs)):
            progress_chain["chain"][n] = folders_queued[
                i*concurrent_runs:concurrent_runs+i*concurrent_runs
            ]
        print(progress_chain)
                
        
        # first_order = d.popleft()
        # return first_order, d

