import re
from tabulate import tabulate # py -m pip install tabulate

# Lexical Analyzer
# Takes user's code and breaks it into tokens
class LexicalAnalyzer:
    def __init__(self, file):
        self.file = file
        self.rules = {}

    # Reads lexemes-tokens text file and stores lexemes-tokens rules in dictionary
    def read_rules(self):
        with open(self.file) as file:
            for line in file:
                (lexeme, token) = line.split()
                self.rules[lexeme] = token

    # Displays invalid token error message
    def invalid_tokens(self, no_matches):
        for position, no_match in no_matches:
            print(f"ERROR: Invalid token '{no_match}' at position {position}.")
        return False

    def filter_matches(self, matches, line):
        last = 0
        no_matches = []
        filtered_matches = []
        # Removes tokens that appear inside strings (might be a better way to do this)
        for current, next, lexeme, token in matches:
            # Skips over tokens w/ positions that do not come after the last token
            if current >= last:
                # Checks for gaps between tokens to find unmatched tokens
                if current - last > 1:
                    no_matches.append((last + 1, line[last:current].strip()))

                filtered_matches.append((current, lexeme, token))
                last = next

        return filtered_matches, no_matches

    # Returns list of matching lexemes
    def get_matches(self, line):
        matches = []
        # Stores matching lexemes with their tokens and line positions in a list
        for lexeme, token in self.rules.items():
            for match in re.finditer(lexeme, line):
                matches.append((match.start(), match.end(), token, match.group()))
        # Sorts lexeme-token pairs based on first appearance in line (PyCharm gave me this)
        matches.sort(key=lambda x: x[0])
        return self.filter_matches(matches, line)

    def get_tokens(self, matches,no_matches):
        self.tokens_order = []
        # Prints and stores tokens in a list to feed to Syntax Analyzer
        for position, token, lexeme in matches:
            if no_matches:
                if no_matches[0][0] <= position:
                    return self.invalid_tokens(no_matches)

            # Prints lexemes and tokens without a table
            print(f"{token}({lexeme})")

            # Repleces KEYWORD tokens with specific token names before storing in list
            if token == "KEYWORD":
                token = f"{lexeme}_KEYWORD"

            self.tokens_order.append(token)

        # Prints lexemes-tokens table (has no descriptions)
        print("\nTable Without Descriptions:")
        swapped_columns = [(lexeme, token) for position, token, lexeme in matches]
        print(tabulate(swapped_columns, headers=["LEXEME", "TOKEN"], tablefmt="fancy_grid",
                       colalign=("center", "center")))
        return True


    # Determines the tokens for the line of code
    def tokenize(self, line):
        # Gets rules dictionary
        self.read_rules()

        # Gets list of matching lexemes
        matches, no_matches = self.get_matches(line)

        # Gets and prints list of tokens
        return self.get_tokens(matches, no_matches)