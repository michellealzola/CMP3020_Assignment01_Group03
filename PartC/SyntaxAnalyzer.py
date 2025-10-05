import re

# Syntax Analyzer
# Takes tokens_order list and checks if order follows grammar rules
class SyntaxAnalyzer:
    def __init__(self, file):
        self.file = file
        self.grammar_rules = {}

    # Reads grammar-rules text file and stores grammar rules in dictionary
    def read_grammar_rules(self):
        with open(self.file) as file:
            for line in file:
                non_terminal, rule = line.split(maxsplit=1)
                rule = rule.strip().replace('"', '').replace("'", "")
                self.grammar_rules[non_terminal] = rule


    # Determines the regex pattern for the full line of code by replacing all non_terminals from grammar rules
    def determine_pattern(self, non_terminal):
        # Checks if non_terminal exists
        if non_terminal not in self.grammar_rules:
            return non_terminal

        # Finds the non_terminal's respective grammar rule / pattern
        pattern = self.grammar_rules[non_terminal]
        # Replaces each non_terminal w/in the grammar rule / pattern with its respective pattern
        for non_ter in self.grammar_rules.keys():
            if non_ter in pattern:
                # Checks again for more non_terminals
                pattern = pattern.replace(non_ter, f"(?:{self.determine_pattern(non_ter)})")
        return pattern

    # Checks if the grammar rules' full regex pattern matches the token_string
    def check_grammar_rules(self, tokens_order):
        # Gets grammar rules dictionary
        self.read_grammar_rules()
        # Creates a string of tokens
        self.tokens_string = " ".join(tokens_order)

        # Checks if expanded regex pattern matches w/ tokens_string
        if re.fullmatch(self.determine_pattern("<stmt>"), self.tokens_string):
            print("Syntax is valid.")
        else:
            print(f"ERROR: Unexpected token.")