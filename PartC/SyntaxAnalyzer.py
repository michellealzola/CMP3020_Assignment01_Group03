from __future__ import annotations
from typing import List, Tuple, Dict, Iterable, Optional
from pathlib import Path

Token = Tuple[str, str]  # (token_type, lexeme)

class ParseError(Exception):
    def __init__(self, message: str, line: int):
        super().__init__(f'Line {line}: {message}')
        self.line = line

class SyntaxAnalyzer:
    def __init__(self, tokens: List[Token], block_termination_path: str = 'block_termination.txt'):
        # keep the NEWLINE
        # enforce ':' NEWLINE after headers
        self.tokens: List[Token] = tokens
        self.i: int = 0
        self.block_endings: Dict[str, str] = self._load_block_terminators(Path(block_termination_path))

    # ---Configuration---
    @staticmethod
    def _load_block_terminators(path: Path) -> Dict[str, str]:
        endings: Dict[str, str] = {}
        if not path.exists():
            new_dic_if_file_is_missing = {'if': 'endif', 'else': 'endif', 'for': 'endfor'}
            return new_dic_if_file_is_missing
        for raw in path.read_text(encoding='utf-8').splitlines():
            line = raw.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                start, end = line.split('=', 1)
                start, end = start.strip(), end.strip()
                if start and end:
                    endings[start] = end

        # if key does not exist in the dictionary, use below defaults
        endings.setdefault('if', 'endif')
        endings.setdefault('else', 'endif')
        endings.setdefault('for', 'endfor')

        return endings
    
    # ---Basic helper functions---
    def _peek(self, n: int = 0) -> Tuple[Optional[str], Optional[str]]:
        if self.i + n < len(self.tokens):
            return self.tokens[self.i + n]
        return None, None

    def _accept(self, token_type: str) -> bool:
        if self._peek()[0] == token_type:
            self.i += 1
            return True
        return False

    def _expect(self, token_type: str) -> Token:
        if self._accept(token_type):
            return self.tokens[self.i - 1]
        got_token, got_value = self._peek()
        self._err(f'Expected {token_type}, got {got_value or got_token!r}')

    # ---Keyword Helpers---
    def _accept_keyword(self, keyword: str) -> bool:
        token, value = self._peek()
        if token == 'KEYWORD' and value == keyword:
            self.i += 1
            return True
        return False

    def _expect_keyword(self, keyword: str) -> None:
        if not self._accept_keyword(keyword):
            got_token, got_value = self._peek()
            self._err(f'Expected {keyword!r}, got {got_value or got_token!r}')

    # ---Skips over NEWLINE tokens---
    def _skip_newlines(self) -> None:
        while self._accept('NEWLINE'):
            pass


    # Keeps reading (parsing) statements one by one
    # until it reaches a keyword that marks the end of the current block
    # such as 'endfor' or 'endif'.
    # This allows nested code block which will be handled properly inside loops or conditionals
    def _parse_statement_list_until(self, end_keywords: Iterable[str]) -> None:
        self._skip_newlines()
        ends = tuple(end_keywords)
        while True:
            token, value = self._peek()
            if token == 'KEYWORD' and value in ends:
                return
            if token is None:
                return
            self.parse_stmt()
            self._expect_stmt_terminator(allow_end_keywords=ends)


    # ---ENTRY POINT---
    # where the syntax analysis begins
    # checks the entire token list (from LexicalAnalyzer)
    # must follow correct Serpent+ grammar

    # Program ::= StatementList
    def parse_program(self) -> bool:
        self._skip_newlines()
        while self._peek()[0] is not None:
            self.parse_stmt()
            self._expect_stmt_terminator()
        return True

    # Statement        ::= Assignment
    #                    | PrintStatement
    #                    | IfStatement
    #                    | ForStatement
    def parse_stmt(self) -> None:
        token, value = self._peek()

        # Ignores the extra NEWLINES safely
        if token == 'NEWLINE':
            self._skip_newlines()
            return

        if token == 'IDENT':
            self.parse_assign()
            return

        if token in ('KEYWORD', 'BUILTIN'):
            if value == 'print':
                self.parse_print()
                return

            # for-block
            if token == 'KEYWORD' and value == 'for':
                self.parse_for_block()
                return

            # if-block
            if token == 'KEYWORD' and value == 'if':
                self.parse_if_block()
                return

            self._err(f'Unexpected keyword: {value!r}')

        self._err(f'Unexpected token: {token!r}')

    # Assignment ::= Identifier "=" Expression
    def parse_assign(self) -> None:
        self._expect('IDENT')
        if self._accept('ASSIGN') or self._accept('AUGASSIGN'):
            self.parse_expr()
            return
        token, value = self._peek()
        self._err(f'Unexpected ASSIGN or AUGASSIGN, got {value or token!r}')


    # PrintStatement   ::= "print" "(" [ ArgumentList ] ")"
    # ArgumentList     ::= Expression { "," Expression }
    def parse_print(self) -> None:
        if not (self._accept('KEYWORD') or self._accept('BUILTIN')):
            self._err('Expected "print"')
        self._expect('LPAREN')
        if self._peek()[0] != 'RPAREN':
            self.parse_expr()
            while self._accept('COMMA'):
                self.parse_expr()
        self._expect('RPAREN')

    # ForStatement     ::= "for" Identifier "in" ListLiteral ":" NEWLINE
    #                      StatementList
    #                      "endfor"
    def parse_for_block(self) -> None:
        self._expect_keyword('for')
        self._expect('IDENT')

        # 'in'
        if not (self._peek()[0] == 'KEYWORD' and self._peek()[1] == 'in'):
            self._err('Expected "in"')
        self.i += 1  # eats 'in'

        self.parse_expr()
        self._expect('COLON')
        self._expect('NEWLINE')
        self._skip_newlines()

        end_for = self.block_endings.get('for', 'endfor')

        self._parse_statement_list_until(end_keywords=(end_for,))
        self._expect_keyword(end_for)

    # IfStatement      ::= "if" Expression ":" NEWLINE
    #                      StatementList
    #                      [ "else" ":" NEWLINE
    #                        StatementList ]
    #                      "endif"
    def parse_if_block(self) -> None:
        self._expect_keyword('if')
        self.parse_expr()
        self._expect('COLON')
        self._expect('NEWLINE')
        self._skip_newlines()

        end_if = self.block_endings.get('if', 'endif')
        else_keyword = 'else'

        # then-block until 'else' or 'endif'
        self._parse_statement_list_until(end_keywords=(else_keyword, end_if))

        # else (optional)
        if self._accept_keyword(else_keyword):
            self._expect('COLON')
            self._expect('NEWLINE')
            self._skip_newlines()
            self._parse_statement_list_until(end_keywords=(end_if,))

        self._expect_keyword(end_if)

    # ListLiteral      ::= "[" [ Number { "," Number } ] "]"
    def parse_list_literal(self) -> None:
        self._expect('LBRACK')
        if self._peek()[0] != 'RBRACK':
            self.parse_expr()
            while self._accept('COMMA'):
                self.parse_expr()
        self._expect('RBRACK')


    # Expression       ::= Term { ("+" | "-") Term }
    # Term             ::= Factor { ("*" | "/") Factor }
    # Factor           ::= Number
    #                    | Identifier
    #                    | String
    #                    | "(" Expression ")"
    def parse_expr(self) -> None:
        self.parse_conditional()

    def parse_conditional(self) -> None:
        self.parse_comparison()
        if self._accept_keyword('if'):
            self.parse_comparison()
            self._expect_keyword('else')
            self.parse_conditional()
            return

    def parse_comparison(self) -> None:
        self.parse_additive()
        while (self._accept('EQEQ') or self._accept('NEQ') or
               self._accept('LT') or self._accept('LE') or
                self._accept('GT') or self._accept('GE')):
            self.parse_additive()

    def parse_additive(self) -> None:
        self.parse_term()
        while self._accept('PLUS') or self._accept('MINUS'):
            self.parse_term()

    def parse_term(self) -> None:
        self.parse_factor()
        while self._accept('STAR') or self._accept('SLASH'):
            self.parse_factor()

    def parse_factor(self) -> None:
        if self._accept('PLUS'):
            self.parse_factor()
            return
        if self._accept('MINUS'):
            self.parse_factor()
            return

        token, _ = self._peek()
        if token in ('IDENT', 'BUILTIN') and self._peek(1)[0] == 'LPAREN':
                self.parse_call()
                return

        if token in ('NUMBER', 'STRING', 'IDENT'):
            self.i += 1
            return

        if token == 'LBRACK':
            self.parse_list_literal()
            return

        if self._accept('LPAREN'):
            self.parse_expr()
            self._expect('RPAREN')
            return

        self._err(f'Unexpected factor: {token!r}')

    def parse_call(self) -> None:
        if self._peek()[0] not in ('IDENT', 'BUILTIN'):
            got, val = self._peek()
            self._err(f'Unexpected function name, got {val or got!r}')
        self.i += 1 # eats name

        self._expect('LPAREN')
        if self._peek()[0] != 'RPAREN':
            self.parse_expr()
            while self._accept('COMMA'):
                self.parse_expr()
        self._expect('RPAREN')

    def _line(self):
        return 1 + sum(1 for k, _ in self.tokens[:self.i] if k == 'NEWLINE')

    def _err(self, message: str) -> None:
        raise ParseError(message, self._line())

    def _expect_stmt_terminator(self, allow_end_keywords: Iterable[str] = ()) -> None:
        token, value = self._peek()
        if token == 'NEWLINE':
            self._skip_newlines()
            return
        if token is None:
            return
        if token == 'KEYWORD' and value in set(allow_end_keywords):
            return

        self._err(f'Expected NEWLINE {", ".join(allow_end_keywords)}, got {value!r}')

