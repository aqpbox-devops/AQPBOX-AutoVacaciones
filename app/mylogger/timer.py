from mylogger.mydecorators import singleton
from mylogger.printer import StatusCode, YLW, WHT
import time

def format_time(value: float) -> str:
    if value >= 1.0:
        return f"{value:.2f} s"
    else:
        milliseconds = value * 1000
        return f"{milliseconds:.2f} ms"
    
@singleton
class TimeCounter:

    total_call_count = 0
    
    def __init__(self):
        self.reset()
        self.accumulated = 0

    def reset(self) -> None:
        self.last_measure = time.time()

    def time(self) -> str:
        temp = self.last_measure
        self.reset()
        diff = self.last_measure - temp
        self.accumulated += diff
        return format_time(diff)

    def total(self) -> None:
        TimeCounter().total_call_count += 1
        print(StatusCode.Debug.format(f"{YLW}{TimeCounter().total_call_count}{WHT} Total time", format_time(self.accumulated)))
        self.accumulated = 0