from interpreter.sintax import ParserToken, AutobotLexer
from mylogger.mydecorators import singleton
from interpreter.functions import *
from mylogger.printer import *
from typing import List
import pandas as pd 

@singleton
class Do2IterDfMann:
    def __init__(self) -> None:
        self.reset()
        self.loop_body: List[ParserToken] = []
        self.last_do = 0

    def eof(self, offset: int=0) -> bool:
        return (self.current_row_idx + offset) >= len(self.current_df)

    def reset(self) -> None:
        self.current_df: pd.DataFrame = None
        self.current_row_idx = 0

    def set_lexer(self, lexer: AutobotLexer) -> None:
        self.lexer = lexer

    def look4do(self) -> None:
        try:
            self.last_do = self.lexer.tokens.index('DoWhileOnDataframe', self.last_do)
        except ValueError:
            pass

        self.reset()

    def getcolumn_by(self, col: str | int) -> str:
        if self.current_dfis is not None:
            col_idx = col

            if isinstance(col, str):
                col_idx = self.current_df.get_loc(col)

            cell = self.current_df.iat[self.current_row_idx, col_idx]

            return str(cell)
        return ''

    def do(self, fn_data: str) -> None:
        try:
            if fn_data.endswith('.xlsx'):
                self.current_df = pd.read_excel(fn_data)
            elif fn_data.endswith('.csv'):
                self.current_df = pd.read_csv(fn_data)
        except FileNotFoundError:
            stfatal(f"Dataframe {CYN}{fn_data}{WHT} source not found.")

    def iterdf(self, action, n_rows) -> None:
        if self.current_df is None:
            return

        if action == 'down':
            self.current_row_idx += n_rows
        
        elif action == 'up':
            self.current_row_idx -= n_rows

        if not self.eof():
            self.lexer.set_at(self.last_do + 2)
        else:
            self.reset()
            self.look4do()

class AutobotCommand:

    COMMANDS = {
        'ExecuteBinary': {'expected': ['LiteralString', 'WaitScreenUpdate'], 
                          'return': 'NoneType',
                          'function': lambda x: open_exe(x)},
        'LeftClickOnImage': {'expected': ['LiteralString', 'WaitScreenUpdate'],
                             'return': 'NoneType',
                             'function': lambda x: find_and_click(x)},
        'WriteText': {'expected': ['LiteralString|GetColumnBy'],
                      'return': 'NoneType',
                      'function': lambda x: write_text(x)},
        'PressKeys': {'expected': ['StoredKeyname|LiteralKeyList'],
                      'return': 'NoneType',
                      'function': lambda x: press_keys(x)},
        'DoWhileOnDataframe': {'expected': ['LiteralString'],
                               'return': 'NoneType',
                               'function': lambda x: Do2IterDfMann().do(x)},
        'IfImageOnScreenDo': {'expected': ['LiteralString', 'ExecuteBinary|LeftClickOnImage|WriteText|PressKeys'],
                              'return': 'bool',
                              'function': lambda x: find_and_click(x, perform_click=False)},
        'IterateDataframe': {'expected': ['StoredKeyname', 'LiteralInteger'],
                             'return': 'NoneType',
                             'function': lambda x, y: Do2IterDfMann().iterdf(x, y)},
        'GetColumnBy': {'expected': ['LiteralInteger|LiteralString'],
                        'return': 'str',
                        'function': lambda x: Do2IterDfMann().getcolumn_by(x)},
        'WaitScreenUpdate': {'expected': ['LiteralInteger|LiteralFloat'],
                             'return': 'NoneType',
                             'function': lambda x: wait_screen_update(None, x)}
    }

    def __init__(self, tokens: List[ParserToken], subcommand: bool=False) -> None:
        self.token_buffer = tokens
        self.command = self.token_buffer.pop(0)
        self.argv: List[ParserToken|AutobotCommand] = []
        self.result: ParserToken = None
        self.error = ''
        self.subcommand = subcommand

    def __repr__(self) -> str:
        return f"{self.command}.({self.argv})"

    def __str__(self) -> str:
        return repr(self)

    def consume(self) -> bool:
        def is_nonterminal(x):
            return x in self.COMMANDS.keys()

        if is_nonterminal(self.command.id):
            expected = self.COMMANDS[self.command.id]['expected']
            stprint(f"Command [{MGT}{self.command.value}{WHT}] expects {YLW}{len(expected)}{WHT} parameters")
            for exp in expected:

                productions = exp.split('|')
                parsed: List[ParserToken|AutobotCommand] = []

                if not self.token_buffer:
                    self.error = f"NotEnoughTokensReceived"
                    return False
                
                for production in productions:

                    if self.token_buffer[0] == production:
                        if is_nonterminal(production):

                            try:
                                sub_command = AutobotCommand(self.token_buffer, subcommand=True)
                            except IndexError:
                                self.error = f"NotEnoughTokensReceived"
                                return False
                            
                            if not procedure_status(f"Sub-command consuming tokens", sub_command, 'consume'):
                                self.error = f"SubcommandError"
                                return False
                            parsed.append(sub_command)
                        else:
                            parsed.append(self.token_buffer.pop(0))

                        break
                
                if not parsed:
                    self.error = f"ExpectedTokenNotFound"
                    return False
                
                self.argv += parsed

            if not self.subcommand and len(self.token_buffer) > 0 and self.token_buffer[0].id != 'NEWLINE':
                self.error = f"Unexpected token {CYN}{self.token_buffer[0].id}{WHT}, left {YLW}{len(self.token_buffer)}{WHT} tokens"
                return False

            return True
        else:
            self.error = f"{MGT}{self.command.id}{WHT} found at {YLW}{self.command.line}:{self.command.col}{WHT} position, is not a valid command"
            return False

    def execute(self) -> bool:
        parameters: List[ParserToken] = []
        function_chain: AutobotCommand = None

        for arg in self.argv:
            if isinstance(arg, ParserToken):
                parameters.append(arg.get_litval())
            elif isinstance(arg, AutobotCommand):
                if self.COMMANDS[arg.command.id]['return'] != 'NoneType':
                    status = procedure_status(f"Executing sub-command [{CYN}{arg.command.id}{WHT}]", arg, 'execute')
                    if status:
                        parameters.append(arg.result)
                    else:
                        self.error = f"Required sub-command {RED}{arg.command.value}{WHT} result failed"
                        return False
                else:
                    function_chain = arg

        sep = f"{WHT}, {YLW}"
        
        stprint(f"Command {MGT}{self.command.value}{WHT}({YLW}{sep.join(map(str, parameters))}{WHT}) execution")
        self.result = self.COMMANDS[self.command.id]['function'](*parameters)
        
        result_t = self.COMMANDS[self.command.id]['return']
        if result_t == 'bool' and self.result != True:
            function_chain = None
        if function_chain is not None:
            status = procedure_status(f"After getting {self.result}, executing post-command [{CYN}{function_chain.command.id}{WHT}]", function_chain, 'execute')
            
            if status:
                return True
            
            self.error = f"Required post-command {RED}{function_chain.command.value}{WHT} result failed"
            return False
        
        return True