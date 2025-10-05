# main_demo.py
from __future__ import annotations
import sys
import argparse
from pathlib import Path
from typing import List, Tuple

from LexicalAnalyzer import LexicalAnalyzer, Token, TokenRow
from SyntaxAnalyzer import SyntaxAnalyzer, ParseError


DEFAULT_SAMPLE = '''\
list = [1, 2, 3]
sum = 0
count = 0

if len(list) != 0:
    for n in list:
        sum += n
        count += 1
    endfor

    average = (sum / count) if count != 0 else 0
    print('The average of the list is', average)
else:
    print('The list is empty.')
endif
'''


def load_code(args: argparse.Namespace) -> str:
    if args.file:
        p = Path(args.file)
        if not p.exists():
            print(f'error: file not found: {p}', file=sys.stderr)
            sys.exit(2)
        return p.read_text(encoding='utf-8')
    if args.code:
        return args.code
    return DEFAULT_SAMPLE


def print_header(title: str) -> None:
    bar = '=' * len(title)
    print(f'\n{title}\n{bar}')


def print_tokens_table(rows: List[TokenRow]) -> None:
    if not rows:
        print('(no tokens)')
        return
    w1 = max(6, max(len(x[0]) for x in rows))
    w2 = max(5, max(len(x[1]) for x in rows))
    print(f'{"Lexeme":<{w1}}  {"Token":<{w2}}  Explanation')
    print('-' * (w1 + w2 + 14))
    for lex, name, expl in rows:
        print(f'{lex:<{w1}}  {name:<{w2}}  {expl}')


def print_raw_tokens(tokens: List[Token]) -> None:
    if not tokens:
        print('(no tokens)')
        return
    for kind, lex in tokens:
        print(f'{kind:>10} : {lex}')


def main() -> None:
    cli = argparse.ArgumentParser(
        description='Serpent+ demo: tokenize and parse source without the GUI.'
    )
    cli.add_argument('--file', '-f', help='Path to a source file to analyze.')
    cli.add_argument('--code', '-c', help='Inline source code string to analyze.')
    cli.add_argument('--show-tokens', action='store_true',
                     help='Show the raw token stream in addition to the token table.')
    cli.add_argument('--no-table', action='store_true', default=False,
                     help='Disable the pretty token table.')
    cli.add_argument('--block-termination', default='block_termination.txt',
                     help='Path to block_termination.txt (default: block_termination.txt)')
    args = cli.parse_args()

    # Load source
    source = load_code(args)

    # Lexical analysis
    print_header('Lexical Analysis')
    lexer = LexicalAnalyzer()
    tokens, lex_errors = lexer.tokenize(source)

    if lex_errors:
        print('Lexical errors:')
        for e in lex_errors:
            print('  -', e)
        sys.exit(1)

    if not args.no_table:
        rows = lexer.tokens_table(tokens)
        print_tokens_table(rows)

    if args.show_tokens:
        print_header('Raw Tokens')
        print_raw_tokens(tokens)

    # Syntax analysis
    print_header('Syntax Analysis')
    try:
        syn = SyntaxAnalyzer(tokens, block_termination_path=args.block_termination)
        syn.parse_program()
        print('Syntax OK')
    except ParseError as e:
        print('Syntax error:', e)
        sys.exit(1)


if __name__ == '__main__':
    main()
