from Token import Token, TokenType, LexerError
class Lexer:
    def __init__(self, text):
        self.text = text; self.pos = 0
        self.current_char = self.text[self.pos] if self.pos < len(self.text) else None
        self.KEYWORDS = {
            'begin': Token(TokenType.BEGIN, 'begin'), 'end': Token(TokenType.END, 'end'),
            'for': Token(TokenType.FOR, 'for'), 'each': Token(TokenType.EACH, 'each'),
            'in': Token(TokenType.IN, 'in'), 'endfor': Token(TokenType.ENDFOR, 'endfor'),
            'print': Token(TokenType.PRINT, 'print'),
        }

    def error(self, message):
        raise LexerError(f"Lexer error: {message} at position {self.pos}")

    def advance(self):
        self.pos += 1
        self.current_char = self.text[self.pos] if self.pos < len(self.text) else None

    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace(): self.advance()

    def skip_comment(self):
        while self.current_char is not None and self.current_char != '\n': self.advance()

    def number(self):
        result = ''
        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char; self.advance()
        return Token(TokenType.NUM, int(result))

    def string_literal(self):
        self.advance(); result = ''
        while self.current_char is not None and self.current_char != '"':
            result += self.current_char; self.advance()
        self.advance()
        return Token(TokenType.STRING, result)

    def _id(self):
        result = ''
        while self.current_char is not None and (self.current_char.isalnum() or self.current_char == '_'):
            result += self.current_char; self.advance()
        return self.KEYWORDS.get(result.lower(), Token(TokenType.ID, result))

    def get_next_token(self):
        while self.current_char is not None:
            if self.current_char.isspace(): self.skip_whitespace(); continue
            if self.current_char == '/' and self.peek() == '/':
                self.advance(); self.advance(); self.skip_comment(); continue
            if self.current_char.isdigit(): return self.number()
            if self.current_char.isalpha() or self.current_char == '_': return self._id()
            if self.current_char == '"': return self.string_literal()
            char_map = {'=': Token(TokenType.ASSIGN, '='), '+': Token(TokenType.PLUS, '+'), '/': Token(TokenType.DIVIDE, '/'), '[': Token(TokenType.LBRACKET, '['), ']': Token(TokenType.RBRACKET, ']')}
            if self.current_char in char_map:
                token = char_map[self.current_char]; self.advance(); return token
            self.error(f"Invalid character '{self.current_char}'")
        return Token(TokenType.EOF, None)

    def peek(self):
        peek_pos = self.pos + 1
        return self.text[peek_pos] if peek_pos < len(self.text) else None

