from Token import TokenType, ParserError

class Parser:
    def __init__(self, lexer, user_input_list):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()
        self.symbol_table = {'numbers_list': user_input_list}

    def error(self, message):
        raise ParserError(f"Parser error: {message}. Found token: {self.current_token}")

    def eat(self, token_type):
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error(f"Expected token {token_type.name}")

    def program(self):
        self.eat(TokenType.BEGIN)
        statement_list = self.parse_statement_list(end_tokens=[TokenType.END])
        self.execute_statement_list(statement_list)
        self.eat(TokenType.END)

    def parse_statement_list(self, end_tokens):
        #Parses a sequence of statements and returns them as a list.
        statements = []
        while self.current_token.type not in end_tokens:
            statements.append(self.parse_statement())
        return statements

    def execute_statement_list(self, statements):
        #Executes a list of pre-parsed statements.
        for statement_type, params in statements:
            if statement_type == 'assign':
                var_name, expr_tokens = params
                self.symbol_table[var_name] = self.evaluate_expression(expr_tokens)
            elif statement_type == 'print':
                string_literal, var_name = params
                value_to_print = self.symbol_table.get(var_name)
                if value_to_print is None: self.error(f"Variable '{var_name}' is not defined.")
                print(f"{string_literal}{value_to_print}")
            elif statement_type == 'for':
                loop_var, list_var, body_statements = params
                iterable_list = self.symbol_table.get(list_var)
                if not isinstance(iterable_list, list): self.error(f"Variable '{list_var}' is not an iterable list.")
                for item in iterable_list:
                    self.symbol_table[loop_var] = item
                    self.execute_statement_list(body_statements)

    def parse_statement(self):
        #Parses a single statement and returns its intermediate representation.
        if self.current_token.type == TokenType.ID:
            return self.parse_assignment()
        elif self.current_token.type == TokenType.FOR:
            return self.parse_for_statement()
        elif self.current_token.type == TokenType.PRINT:
            return self.parse_print_statement()
        else:
            self.error("Invalid start of a statement")

    def parse_assignment(self):
        var_name = self.current_token.value
        self.eat(TokenType.ID)
        self.eat(TokenType.ASSIGN)
        #Capture the expression tokens without evaluating them yet
        expr_tokens = []
        #Simple expression capture: assumes term, op, term or just term
        expr_tokens.append(self.current_token)
        self.eat(self.current_token.type)
        if self.current_token.type in (TokenType.PLUS, TokenType.DIVIDE):
            expr_tokens.append(self.current_token)
            self.eat(self.current_token.type)
            expr_tokens.append(self.current_token)
            self.eat(self.current_token.type)
        return ('assign', (var_name, expr_tokens))

    def parse_for_statement(self):
        self.eat(TokenType.FOR); self.eat(TokenType.EACH)
        loop_variable_name = self.current_token.value
        self.eat(TokenType.ID); self.eat(TokenType.IN)
        list_variable_name = self.current_token.value
        self.eat(TokenType.ID)
        
        #Parse the body statements once and store them
        body_statements = self.parse_statement_list(end_tokens=[TokenType.ENDFOR])
        
        self.eat(TokenType.ENDFOR)
        return ('for', (loop_variable_name, list_variable_name, body_statements))

    def parse_print_statement(self):
        self.eat(TokenType.PRINT)
        string_to_print = self.current_token.value
        self.eat(TokenType.STRING); self.eat(TokenType.PLUS)
        variable_name = self.current_token.value
        self.eat(TokenType.ID)
        return ('print', (string_to_print, variable_name))

    def evaluate_expression(self, tokens):
        #Evaluates a list of tokens representing an expression.
        if len(tokens) == 1:
            return self.evaluate_term(tokens[0])
        
        left_val = self.evaluate_term(tokens[0])
        op = tokens[1]
        right_val = self.evaluate_term(tokens[2])
        
        if op.type == TokenType.PLUS:
            return left_val + right_val
        elif op.type == TokenType.DIVIDE:
            if right_val == 0: self.error("Division by zero")
            return left_val / right_val

    def evaluate_term(self, token):
        #Evaluates a single term token.
        if token.type == TokenType.NUM:
            return token.value
        elif token.type == TokenType.ID:
            val = self.symbol_table.get(token.value)
            if val is None: self.error(f"Variable '{token.value}' is not defined")
            return val
        else:
            self.error("Invalid term in expression")

    def interpret(self):
        #The entry point for the interpreter.
        self.program()