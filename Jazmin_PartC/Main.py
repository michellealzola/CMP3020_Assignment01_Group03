import sys
from LexicalAnalyzer import Lexer, LexerError
from Parser import Parser, ParserError

def main():
    #my pseudo code
    source_code = """
    begin
        sum = 0
        count = 0
        for each number in numbers_list
            sum = sum + number
            count = count + 1
        endfor
        average = sum / count
        print "The average of the list of numbers is " + average
    end
    """
    print("--- Average Calculator ---")
    print("This program calculates the average of a list of numbers you give it.")
    
    while True:
        try:
            user_input = input("\nPlease enter a list of numbers separated by spaces (or 'q' to quit): ")
            if user_input.lower() == 'q':
                print("Exiting the program. Goodbye!"); break
            if not user_input:
                print("You entered an empty list. The average is undefined."); continue
            
            numbers = [float(num) for num in user_input.split()]
            
            lexer = Lexer(source_code)
            interpreter = Parser(lexer, numbers)
            interpreter.interpret()
        except ValueError:
            print("Error: Invalid input. Please enter only numbers separated by spaces.")
        except (LexerError, ParserError) as e:
            print(f"An internal error occurred: {e}", file=sys.stderr)
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

if __name__ == '__main__':
    main()