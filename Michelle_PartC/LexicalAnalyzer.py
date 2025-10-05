import re
from pathlib import Path
from typing import List, Dict, Tuple

Token = Tuple[str, str]
TokenRow = Tuple[str, str, str]

class LexicalAnalyzer:
    def __init__(
            self,
            token_lexeme_path: str = 'token_lexeme.txt',
            token_translation_path: str = 'token_translation.txt',
            keyword_path: str = 'keywords.txt',
            builtin_path: str = 'builtin.txt'
        ):
        self.token_lexeme_path = Path(token_lexeme_path)
        self.token_translation_path = Path(token_translation_path)
        self.keyword_path = Path(keyword_path)
        self.builtin_path = Path(builtin_path)

        self.token_map: Dict[str, Tuple[str, str]] = self._load_token_map()
        self.master_re = self._build_master_regex()

    # ---Line helper---
    # Returns only useful lines (not blank, not comments - starting with #, no leading or trailing spaces)
    def _load_lines(self, path: Path) -> List[str]:
        return [
            line.strip() for line in path.read_text(encoding='utf-8').splitlines()
            if line.strip() and not line.strip().startswith('#')
        ]

    # ---Reads token_translation.txt---
    # from
    # KEYWORD|Keyword|Language reserved word
    # to
    # { "KEYWORD": ("Keyword", "Language reserved word")}
    def _load_token_map(self) -> Dict[str, Tuple[str, str]]:
        token_map: Dict[str, Tuple[str, str]] = {}
        # the ':' here introduces a type hint (what type this variable should hold)
        # the expected data type is Dict[str, Tuple[str, str]]
        for line in self._load_lines(self.token_translation_path):
            parts = line.split('|')
            if len(parts) >= 3:
                token_type, token_name, token_description = parts[0].strip(), parts[1].strip(), parts[2].strip()
                token_map[token_type] = (token_name, token_description)
        return token_map

    # ---Create regex (regular expression) PATTERN---
    # to match any one of the possible words in keywords.txt and builtin.txt
    # from -->
    # if
    # else
    # for
    # endfor
    # endif
    # to -->
    # "endfor|endif|else|for|if"
    def _build_master_regex(self) -> re.Pattern:
        keyword = [re.escape(x) for x in self._load_lines(self.keyword_path)]
        builtin = [re.escape(x) for x in self._load_lines(self.builtin_path)]

        keyword_union = '|'.join(sorted(keyword, key=len, reverse=True)) or r'(?!x)x'
        builtin_union = '|'.join(sorted(builtin, key=len, reverse=True)) or r'(?!x)x'
        # r'(?!x)x' means instead of crashing, use this placeholder when the document that was read from is empty

        token_specifications: List[Tuple[str, str]] = []
        for line in self._load_lines(self.token_lexeme_path):
            if '=' not in line:
                continue
            name, pattern = line.split('=', 1)
            name, pattern = name.strip(), pattern.strip()
            pattern = pattern.replace('{KEYWORDS}', keyword_union).replace('{BUILTIN}', builtin_union)
            token_specifications.append((name, pattern))

        # Sort by length (longer patterns first) and wrap each in a named group
        group = [f'(?P<{n}>{p})' for n, p in token_specifications]
        return re.compile('|'.join(group))

    def tokenize(self, text: str) -> Tuple[List[Token], List[str]]:
        tokens: List[Token] = []
        errors: List[str] = []
        for match in self.master_re.finditer(text):
            token_type = match.lastgroup
            lexeme = match.group()

            if token_type in ('SKIP', 'NEWLINE'):
                if token_type == 'NEWLINE':
                    tokens.append(('NEWLINE', '\\n'))
                continue  # ignored SKIP (whitespace) tokens; only preserve NEWLINE

            if token_type in ('BADSEQ', 'MISMATCH'):
                errors.append(f'Error, {lexeme!r} is not a valid token')
                continue

            if token_type is None:
                continue

            tokens.append((token_type, lexeme))

        return  tokens, errors

    def describe_token(self, kind: str) -> Tuple[str, str]:
        return self.token_map.get(kind, (kind, ''))

    def tokens_table(self, tokens: List[Token]) -> List[TokenRow]:
        rows: List[TokenRow] = []
        for token_type, lexeme in tokens:
            name, description = self.describe_token(token_type)
            rows.append((lexeme, name, description))
        return rows

