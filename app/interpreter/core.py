from mylogger.printer import *
from interpreter.sintax import AutobotLexer
from interpreter.semantic import AutobotCommand, Do2IterDfMann
import os

class AutobotCore:
    def __init__(self, fn_code: str) -> None:
        self.fn = fn_code
        self.code = ''
        self.error = ''

    def read_file(self):
        if not os.path.isfile(self.fn):
            self.error = 'FileNotFound'
            return False

        with open(self.fn, 'r', encoding='utf-8') as file:
            self.code = file.read()
        return True
    
    def execute(self):
        stenvmsg('Reading and Scanning tokens')

        code_read = procedure_status(f"Code read from {self.fn}", self, 'read_file')

        if code_read:

            self.lexer = AutobotLexer(self.code)
            Do2IterDfMann().set_lexer(self.lexer)
            scanned = procedure_status('Code scan', self.lexer, 'tokenize')

            TimeCounter().total()
            if code_read and scanned:
                stenvmsg(GRN + 'Bot ready!')

                Do2IterDfMann().look4do()

                while not self.lexer.eof():
                    tokens = self.lexer.next_token_ocurrence('NEWLINE')
                    command = AutobotCommand(tokens)
                    consume_status = procedure_status(f"Consuming tokens. Left: {YLW}{len(tokens)}{WHT} tokens", command, 'consume')
                    if not consume_status:
                        TimeCounter().total()
                        break
                    procedure_status('Processing command', command, 'execute')
                    TimeCounter().total()
            else:
                stenvmsg(RED + 'Unable to run bot')

        stenvmsg(GRY + 'EOF reached. Shutting down!')