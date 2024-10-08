from colorama import Fore as cfo
from colorama import init
from mylogger.error_handler import get_error
from typing import List
import sys

init()

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
    Running = GRN+'[ RUN      ]'+WHT+' {}'+WHT
    Success = GRN+'[ .     OK ]'+WHT+' {} ({})'+WHT
    Failed  = RED+'[  FAILED  ]'+WHT+' {} ({})'+WHT
    Error   = RED+'[ .  ERROR ]'+WHT+' {}'+WHT
    Fatal   = RED+'[ ---FATAL ]'+WHT+' {}'+WHT
    Print   = GRN+'[          ]'+WHT+' {} ({})'+WHT
    Debug   = GRN+'[----------]'+WHT+' {} ({})'+WHT
    EnvMsg  = GRN+'[==========]'+WHT+' {}'+WHT

from mylogger.timer import TimeCounter

def stprint(msg: str) -> None:
    print(StatusCode.Print.format(msg, TimeCounter().time()))

def stdebug(msg: str) -> None:
    print(StatusCode.Debug.format(msg, TimeCounter().time()))

def stfatal(msg: str) -> None:
    print(StatusCode.Fatal.format(msg, TimeCounter().time()))
    sys.exit(0)

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