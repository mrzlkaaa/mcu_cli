from rich.tree import Tree as RTree
from rich.table import Table
from rich import print as rprint
from rich.text import Text


class Display():
    def __init__(self):
        return

    def tree(
        self, 
        structure: dict
    ) -> None:
        for parent, entry_level in structure.items():
            tree = RTree("📁" + parent)
            for keys, sub_level in entry_level.items():
                entry = tree.add("📁" + keys)
                for sub_files in sub_level:
                    entry.add(sub_files)
        rprint(tree)
        
    def table(
        self,
        cols: list,
        rows: list,
        title:str | None=None,
        **kwargs #*for customization

    ) -> None:
        #* Table initialization
        table = Table(title=title)
        for _, c in enumerate(cols):
            table.add_column(c)

        for _, r in enumerate(rows):
            table.add_row(*r)
        
        rprint(table)