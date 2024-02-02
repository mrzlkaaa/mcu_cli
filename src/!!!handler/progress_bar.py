from .main import  Handler
from colorama import Back

#todo getter/setter required
class Progress_bar(Handler):
    LENGTH:float = 70.0

    def __init__(self, share, current_step, steps, file, success=None):
        self._progress = float(share/100)
        self._current_step = current_step
        self.steps = steps
        self.file = file
        self._success = True if success is None else success
        self.color=Back.CYAN if self.success else Back.RED

    @property
    def progress(self):
        return self._progress

    @progress.setter
    def progress(self, val):
        self._progress = float(val/100)

    @property
    def current_step(self):
        return self._current_step

    @current_step.setter
    def current_step(self, val):
        self._current_step = val

    @property
    def success(self):
        return self._success

    @success.setter
    def success(self, val):
        self._success = val
        self.color=Back.CYAN if self.success else Back.RED
    

    def print_res(self):
        progress_filled = self.color + int(self.progress*self.LENGTH)*' ' + Back.RESET
        not_filled = int(self.LENGTH-int(self.progress*self.LENGTH))*"."
        template = f"\r|{progress_filled}{not_filled}| {self.progress*100:.1f}% | {self.current_step}/{self.steps} - ./{self.file}" #! there is a little bug for long file namespacing
        self.clear_line()
        return print(template, end="\r")
    
    def clear_line(self):
        return print("\r"+''*int(self.LENGTH), end="\r")