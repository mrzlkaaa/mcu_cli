from .main import  Handler
from colorama import Back

class Progress_bar(Handler):
    LENGTH:float = 70.0

    def __init__(self, share, current_step, steps, file, success=True):
        self.progress = float(share/100)
        self.current_step = current_step
        self.steps = steps
        self.file = file
        self.color=Back.CYAN if success else Back.RED

    def print_res(self):
        progress_filled = self.color + int(self.progress*self.LENGTH)*' ' + Back.RESET
        not_filled = int(self.LENGTH-int(self.progress*self.LENGTH))*"."
        template = f"\r|{progress_filled}{not_filled}| {self.progress*100:.1f}% | {self.current_step}/{self.steps} - ./{self.file}" #! there is a little bug for long file namespacing
        self.clear_line()
        print(template, end="\r")
    
    def clear_line(self):
        print("\r"+''*self.LENGTH, end="\r")