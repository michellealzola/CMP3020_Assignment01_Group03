# CMPP 3020 Assignment 1 - Concepts, Syntax, and Lexical Analysis
## By Group 3, CMPP 3020 BSA, Fall 2025 - BTech
### Michelle, Umaya, Altamish, Jazmin, Mihir, Nathan

## Overview
This project is a simple lexical analyzer and parser for Serpent+, a custom, Python-inspired programming language. The repository contains our work for Parts B and C of the assignment, culminating in a graphical user interface (GUI) that allows users to write, analyze, and debug Serpent+ code.

The application processes the input code, performs a lexical analysis to break it into tokens, and then parses it to verify its syntactic correctness according to the language's grammar.


## The Serpent+ Language
Serpent+ was designed as an educational language that blends Python's readability with the structural clarity of explicit block terminators (e.g., endfor, endif). This makes the language's grammar unambiguous and easier to analyze.

## Full Language Rules: The documentation for the Serpent+ language we created can be found in the: [serpent_language_documentation.md](https://github.com/michellealzola/CMP3020_Assignment01_Group03/blob/master/PartC/serpent_language_documentation.md)
## Token Lexemes:  The valid lexemes and tokens this program analyzes can be found in the [token_lexeme.txt](https://github.com/michellealzola/CMP3020_Assignment01_Group03/blob/4f30f089707ceb49d89eeb7685bf98a4136f7101/PartC/token_lexeme.txt) 
file. 

The [average.md](https://github.com/michellealzola/CMP3020_Assignment01_Group03/blob/0601e776ad271492fe6830a901bbb514a0068cf0/PartB/average.md)
file located in the [PartB](https://github.com/michellealzola/CMP3020_Assignment01_Group03/blob/0601e776ad271492fe6830a901bbb514a0068cf0/PartB) folder contains our pseudocode, BNF and EBNF rules, and parse trees.

## Assignment Components
## Part B: Syntax Description
This part contains the theoretical groundwork for the Serpent+ language, the [average.md](https://github.com/michellealzola/CMP3020_Assignment01_Group03/blob/0601e776ad271492fe6830a901bbb514a0068cf0/PartB/average.md)
file located in the [PartB](https://github.com/michellealzola/CMP3020_Assignment01_Group03/blob/0601e776ad271492fe6830a901bbb514a0068cf0/PartB) folder contains our pseudocode, BNF and EBNF rules, and parse trees.

## Part C: Lexical Analyzer & Parser
This is the main application, a simple lexical analyzer and parser program written in Python to analyze our own Python-inspired language, Serpent+. We have created a GUI that allows users to test their Serpent+ code to check for correct syntax and view error messages. All related files are located in the [PartC](https://github.com/michellealzola/CMP3020_Assignment01_Group03/blob/4f30f089707ceb49d89eeb7685bf98a4136f7101/PartC) folder.
 

### How to Run the Program
To run the program, download and unzip the SerpentPlus.zip folder which can be found _____. Inside contains the SerpentPlus.exe which can be double-clicked to launch.

### Serpent+ GUI Preview
![SerpentPlusGUI_Screenshot.png](SerpentPlusGUI_Screenshot.png)

## Navigating The GUI
Within the application, the main function is to insert your code syntax into the text box given to the user, then press the 'Analyze' button and the application will return a token list of the syntax of the code the user provided. If the syntax passes, you will recieve a 'synatax analysis completed successfully', if an error occurs within analyzing the grammer of your syntax, a applicable error will arise and the line of code that spawned the error will be highlighted.

If the user wishes to continue to use the application, simply press the 'reset' button located next to the 'analyze' button and add as much code as you'd like!

## Built With
[Python 3.13.7](https://www.python.org/downloads/release/python-3137/) (Python Version)\
[PyCharm](https://www.jetbrains.com/pycharm/) (Python IDE)\
[PySide6](https://pypi.org/project/PySide6/) (GUI)


### Serpent+ GUI Preview
![SerpentPlusGUI_Screenshot.png](SerpentPlusGUI_Screenshot.png)