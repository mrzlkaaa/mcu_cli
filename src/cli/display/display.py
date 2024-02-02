from rich.tree import Tree
from rich.table import Table
from rich.console import Console
from rich.text import Text
from rich.theme import Theme
from rich.progress import Progress
import time

import asyncio

from concurrent.futures import ThreadPoolExecutor

class Display():
    THEME = Theme({
        "default" : "cyan",
        "good": "bold green",
        "warning": "yellow",
        "danger": "bold red"
    })

    def __init__(self):
        #! It's better move to functions / add functionality to replace themes
        self.console = Console(theme=self.THEME)
        return

    def tree(
        self, 
        structure: dict
    ) -> None:

        for parent, entry_level in structure.items():
            tree = Tree("📁" + parent)
            for keys, sub_level in entry_level.items():
                entry = tree.add("📁" + "[bold]" + keys)
                for sub_files in sub_level:
                    entry.add(sub_files)
        self.console.print(tree)
        
    def table(
        self,
        cols: list,
        rows_data: list,
        title:str | None=None
    ) -> None:

        #* Table initialization
        table = Table(title=title)

        for _, c in enumerate(cols):
            table.add_column(c)

        for _, r in enumerate(rows_data):
            *row, style_key = r
            table.add_row(*row, style=style_key)
        
        self.console.print(table)

    def progress_bar(self, **kwargs):
        # with Progress() as progress:

        #     task1 = progress.add_task("[red]Downloading...", total=1000)
        #     task2 = progress.add_task("[green]Processing...", total=1000)
        #     task3 = progress.add_task("[cyan]Cooking...", total=1000)

        #     while not progress.finished:
        #         progress.update(task1, advance=10)
        #         progress.update(task2, advance=0.3)
        #         progress.update(task3, advance=0.9)
        #         time.sleep(1)


        return Progress(**kwargs)

    def status(
        self,
        status_text:str,
        finished_text: str | None = None,
        sleep_time: int = 3
    ):
        
        with self.console.status(f"[bold green]{status_text}") as _:
            time.sleep(sleep_time)
            if finished_text:
                self.console.print(finished_text)
        
    def text(
        self,
        text:str,
        style:str="default"
    ):
        t = Text()
        t.append(
            text,
            style=style
        )
        
        self.console.print(t)
    

if __name__ == "__main__":

    with ThreadPoolExecutor(max_workers=4) as executor:
            for n in range(3):
                executor.submit(
                    Display().status,
                    f"Calculation {n} running...",
                    f"Calculation {n} started successfully",
                    2
                    
                )
        