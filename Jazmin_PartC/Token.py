from enum import Enum

class TokenType(Enum):
    BEGIN = 'BEGIN'; END = 'END'; FOR = 'FOR'; EACH = 'EACH'; IN = 'IN'
    ENDFOR = 'ENDFOR'; PRINT = 'PRINT'; NUM = 'NUM'; STRING = 'STRING'
    ID = 'ID'; PLUS = '+'; DIVIDE = '/'; ASSIGN = '='; LBRACKET = '['
    RBRACKET = ']'; EOF = 'EOF'

class Token:
    def __init__(self, type, value):
        self.type = type; self.value = value
    def __str__(self):
        return f'Token({self.type.name}, {repr(self.value)})'

class LexerError(Exception): pass
class ParserError(Exception): pass