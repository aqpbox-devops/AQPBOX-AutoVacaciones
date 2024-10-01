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
        'PressKeys': {'expected': ['StoredKeyname', 'KeynameChain'],
                      'return': 'NoneType',
                      'function': lambda x: x},
        'KeynameChain': {'expected': ['StoredKeyname|EPSILON', 'KeynameChain'],
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

    def __init__(self, tokens: List[ParserToken]) -> None:
        self.token_buffer = tokens
        self.command = self.token_buffer.pop(0)
        self.argv: List[List[ParserToken|AutobotCommand]] = []
        self.result: ParserToken = None
        self.error = ''

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
                
                epsilon_found = False
                
                for production in productions:
                    if production == 'EPSILON':
                        epsilon_found = True
                        continue

                    if self.token_buffer[0] == production:
                        if is_nonterminal(production):

                            try:
                                sub_command = AutobotCommand(self.token_buffer)
                            except IndexError:
                                self.error = f"NotEnoughTokensReceived"
                                return False
                            
                            procedure_status(f"Sub-command consuming tokens", sub_command, 'consume')
                            parsed.append(sub_command)
                        else:
                            parsed.append(self.token_buffer.pop(0))
                if not parsed and not epsilon_found:
                    self.error = f"ExpectedTokenNotFound"
                    return False
                
                self.argv.append(parsed)
                print(self.argv)

            return True
        else:
            self.error = f"{MGT}{self.command.id}{WHT} found at {YLW}{self.command.line}:{self.command.col}{WHT} position, is not a valid command"
            return False

    def execute(self) -> bool:
        parameters: List[ParserToken] = []
        function_chain: AutobotCommand = None

        for arg in self.argv:
            print(arg)
            if not arg:
                break
            for rep in arg:
                if isinstance(rep, ParserToken):
                    parameters.append(rep.value)
                elif isinstance(rep, AutobotCommand):
                    if self.COMMANDS[rep.command.id]['return'] != 'NoneType':
                        status = procedure_status(f"Executing sub-command [{CYN}{rep.command.id}{WHT}]", rep, 'execute')
                        if status:
                            parameters.append(rep.result)
                        else:
                            self.error = f"Required sub-command {RED}{rep.command.value}{WHT} result failed"
                            return False
                    else:
                        function_chain = rep

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