from mylogger.printer import *
import re

class ParserToken:
    class Keyword:
        def __init__(self, value: str) -> None:
            self.value = value

        def __repr__(self) -> str:
            return f"{CYN}KeyId{WHT}[{MGT}{repr(self.value)[1:-1]}{WHT}]"
        
        def __str__(self):
            return self.value
            

    def __init__(self, id: str, value: str='', line: int=0, col: int=0) -> None:
        self.id = id
        self.line = line
        self.col = col
        if id.__contains__('Integer'):
            self.value = int(value)
        elif id.__contains__('Float'):
            self.value = float(value)
        elif id.__contains__('String'):
            self.value = value[1:-1]
        else:
            self.value = self.Keyword(value)

    def __eq__(self, other: object):
        if isinstance(other, ParserToken):
            return self.id == other.id
        if isinstance(other, str):
            return self.id == other
        raise NotImplementedError

    def __repr__(self) -> str:
        return f"{CYN}TOKEN{WHT}<{MGT}{self.id}{WHT}[{YLW}{self.line}:{self.col}{WHT}], {MGT}{type(self.value).__name__}{WHT}({self.value})>"

class AutobotLexer:
    def __init__(self, code: str) -> None:
        self.code = code + '\n'
        self.tokens: List[ParserToken] = []
        self.current_position = 0
        self.error = ''

    def next_jumpline(self) -> List[ParserToken]:
        try:
            found_at = self.tokens.index('NEWLINE', self.pos)
        except ValueError:
            chunk = self.tokens[self.pos:]
            self.pos = len(self.tokens)
            return chunk
        
        chunk = self.tokens[self.pos:self.pos+found_at]
        self.pos = found_at + 1
        return chunk
    
    def eof(self) -> bool:
        return self.pos >= len(self.tokens)

    def tokenize(self) -> bool:
        patterns = {
            'ExecuteBinary': r'START',
            'LeftClickOnImage': r'CLICK',
            'WriteText': r'INPUT',
            'PressKeys': r'PRESS',
            'DoWhileOnDataframe': r'DO',
            'IfImageOnScreenDo': r'IFIOS',
            'IterateDataframe': r'ITERDF',
            'LiteralFloat': r'\d+\.\d+',         # Flotantes
            'LiteralInteger': r'\b\d+\b',        # Enteros (evitar puntos decimales)
            'LiteralString': r'\'[^\']*\'',      # Cadenas entre comillas simples
            'GetColumnBy': r'\$',              # Token '$'
            'WaitScreenUpdate': r'\!',              # Token '!'
            'StoredKeyname': r'[a-zA-Z_][a-zA-Z0-9_]*',  # Keys
            'NEWLINE': r'\n',
            'ONECOMMENT':  r'--([\s\S]*?)\n',
            'MULTICOMMENT': r'-<[\s\S]*?(>-|\n?$)',
            'SKIP': r'[ \t]+',            # Espacios y tabulaciones
        }

        line = 1
        offset = 0
        while self.current_position < len(self.code):
            match = None
            for token_type, pattern in patterns.items():
                regex = re.compile(pattern)
                match = regex.match(self.code, self.current_position)
                if match:
                    text = match.group(0)
                    forward = len(text)

                    if token_type == 'ONECOMMENT':
                        forward -= 1
                        
                    if token_type not in ['SKIP', 'ONECOMMENT', 'MULTICOMMENT']:
                        if not (token_type == 'NEWLINE' and 
                                (not self.tokens or self.tokens[-1].id == 'NEWLINE')):
                            self.tokens.append(ParserToken(token_type, text, line, offset))
                    
                    if token_type == 'NEWLINE':
                        line += 1
                        offset = 0

                    else:
                        offset += forward

                    self.current_position += forward
                    break

            if not match:
                self.error = f"BadToken[at({YLW}{line}:{offset}{WHT}), {MGT}char{WHT}({self.code[self.current_position]})]"
                return False

        count = len(self.tokens)
        if count > 0:
            self.pos = 0
            stprint(f"Tokens count {count}")
            return True
        
        self.error = 'EmptyCode'
        return False
    