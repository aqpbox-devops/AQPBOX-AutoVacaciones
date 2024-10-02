from colorama import Fore as cfo
from mylogger.error_handler import get_error
from typing import List

GRN = cfo.GREEN
RED = cfo.RED
WHT = cfo.RESET
CYN = cfo.CYAN
MGT = cfo.MAGENTA
YLW = cfo.YELLOW
GRY = cfo.WHITE
BLE = cfo.BLUE
LMG = cfo.LIGHTMAGENTA_EX

class StatusCode:
    Running = GRN+'[ RUN      ]'+WHT+' {}'
    Success = GRN+'[ .     OK ]'+WHT+' {} ({})'
    Failed  = RED+'[  FAILED  ]'+WHT+' {} ({})'
    Error   = RED+'[ .  ERROR ]'+WHT+' {}'
    Fatal   = RED+'[ ---FATAL ]'+WHT+' {}'
    Print   = GRN+'[          ]'+WHT+' {} ({})'
    Debug   = GRN+'[----------]'+WHT+' {} ({})'
    EnvMsg  = GRN+'[==========]'+WHT+' {}'

from mylogger.timer import TimeCounter

def stprint(msg: str) -> None:
    print(StatusCode.Print.format(msg, TimeCounter().time()))

def stdebug(msg: str) -> None:
    print(StatusCode.Debug.format(msg, TimeCounter().time()))

def stfatal(msg: str) -> None:
    print(StatusCode.Fatal.format(msg, TimeCounter().time()))
    exit(0)

def stenvmsg(msg: str) -> None:
    TimeCounter().reset()
    print(StatusCode.EnvMsg.format(msg))

def procedure_status(msg: str, obj: object, method_name: str) -> str:

    print(StatusCode.Running.format(f"Running {LMG}{(type(obj).__name__)}{YLW}.{BLE}{method_name}{WHT}()"))
        
    method = getattr(obj, method_name)

    TimeCounter().reset()
    value = method()
    exec_time = TimeCounter().time()
    
    if not value:
        print(StatusCode.Failed.format(msg, exec_time))
        print(StatusCode.Error.format(get_error(obj)))
    else:
        print(StatusCode.Success.format(msg, exec_time))

    return value