from interpreter.sintax import ParserToken
from interpreter.functions import *
from mylogger.printer import *
from typing import List

class AutobotCommand:

    COMMANDS = {
        'ExecuteBinary': {'expected': ['LiteralString', 'WaitScreenUpdate'], 
                          'return': 'NoneType',
                          'function': lambda x: x},
        'LeftClickOnImage': {'expected': ['LiteralString', 'WaitScreenUpdate'],
                             'return': 'NoneType',
                             'function': lambda x: x},
        'WriteText': {'expected': ['LiteralString|GetColumnBy'],
                      'return': 'NoneType',
                      'function': lambda x: x},
        'PressKeys': {'expected': ['StoredKeyname|LiteralKeyList'],
                      'return': 'NoneType',
                      'function': lambda x: x},
        'DoWhileOnDataframe': {'expected': ['LiteralString'],
                               'return': 'NoneType',
                               'function': lambda x: x},
        'IfImageOnScreenDo': {'expected': ['LiteralString', 'ExecuteBinary|LeftClickOnImage|WriteText|PressKeys'],
                              'return': 'NoneType',
                              'function': lambda x: x},
        'IterateDataframe': {'expected': ['StoredKeyname', 'LiteralInteger'],
                             'return': 'NoneType',
                             'function': lambda x, y: (x, y)},
        'GetColumnBy': {'expected': ['LiteralInteger|LiteralString'],
                        'return': 'str',
                        'function': lambda x: 'STRING DE PRUEBA'},
        'WaitScreenUpdate': {'expected': ['LiteralInteger|LiteralFloat'],
                             'return': 'NoneType',
                             'function': lambda x: x}
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
                parameters.append(arg.value)
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
        
        if function_chain is not None:
            status = procedure_status(f"Executing post-command [{CYN}{function_chain.command.id}{WHT}]", function_chain, 'execute')
            
            if status:
                return True
            
            self.error = f"Required post-command {RED}{function_chain.command.value}{WHT} result failed"
            return False
        
        return True