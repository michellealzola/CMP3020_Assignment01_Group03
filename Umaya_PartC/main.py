from LexicalAnalyzer import LexicalAnalyzer
from SyntaxAnalyzer import SyntaxAnalyzer
# Main Driver
# Analyzes line of code from user
def main():
    line = ""
    # Reads files
    lexical_analyzer = LexicalAnalyzer("lexemes_data.txt")
    syntax_analyzer = SyntaxAnalyzer("grammar_rules.txt")

    while line != "q":
        # Gets line of code from user
        line = input("\nEnter a line of code (q to quit): ")
        if line.lower() == "q":
            continue

        # Starts lexical analysis by passing in user's line of code
        valid_tokens = lexical_analyzer.tokenize(line)
        # Prevents Syntax Analysis from running if there are invalid tokens
        if not valid_tokens:
            continue
        # Starts syntax analysis by passing in tokens list
        syntax_analyzer.check_grammar_rules(lexical_analyzer.tokens_order)

if __name__ == "__main__":
    main()