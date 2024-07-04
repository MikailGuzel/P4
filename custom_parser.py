import logging
from dictionary import Dictionary
from parser_nodes import AssignmentNode, DeleteNode, ExpressionNode, NumberNode, StringNode, IfNode, CellReferenceNode

logger = logging.getLogger(__name__)

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_line = 0  # to keep track of the current line index

    def _split_into_lines(self, tokens):
        lines = []
        current_line = []
        for token in tokens:
            if token.type == Dictionary.NEWLINE:
                if current_line:
                    lines.append(current_line)
                current_line = []
            else:
                current_line.append(token)
        if current_line:
            lines.append(current_line)  # add the last line if not empty
        return lines

    def parse_line(self, line):
        """Parses a single line of tokens into a node."""
        print(f"Parsing line: {line}")
        if not line:
            return None  # handle empty lines
        first_token = line[0]
        print(first_token)
        if first_token.type == Dictionary.KEYWORD and first_token.value == 'if':
            return self.parse_if_statement(line)
        elif first_token.type == Dictionary.KEYWORD and first_token.value == 'delete':
            return self.parse_delete(line)
        elif first_token.type == Dictionary.IDENTIFIER or first_token.type == Dictionary.CELL:
            return self.parse_assignment(line)
        else:
            return self.parse_expression(line)


    def parse_expression(self, tokens):
        # remove all ws tokens
        tokens = [token for token in tokens if token.type != Dictionary.WHITE_SPACE]
        node, _ = self.parse_addition_subtraction(tokens)
        return node

    def parse_addition_subtraction(self, tokens):
        node, consumed = self.parse_multiplication_division(tokens)
        i = consumed
        while i < len(tokens):
            if tokens[i].type == Dictionary.PLUS or tokens[i].type == Dictionary.MINUS:
                operator = tokens[i].type
                i += 1
                right, consumed_right = self.parse_multiplication_division(tokens[i:])
                node = ExpressionNode(node, operator, right)
                i += consumed_right
                break  # handle multiple operations as needed
        return node, i

    def parse_multiplication_division(self, tokens):
        node, consumed = self.parse_primary(tokens)
        i = consumed
        while i < len(tokens):
            if tokens[i].type == Dictionary.MULTIPLICATION or tokens[i].type == Dictionary.DIVISION:
                operator = tokens[i].type
                i += 1
                right, consumed_right = self.parse_primary(tokens[i:])
                node = ExpressionNode(node, operator, right)
                i += consumed_right
            break  # handle multiple operations as needed
        return node, i

    def parse_primary(self, tokens):
        token = tokens[0]
        if token.type == Dictionary.INTEGER:
            return NumberNode(token.value), 1
        elif token.type == Dictionary.STRING:
            return StringNode(token.value), 1
        elif token.type == Dictionary.CELL:
            return self.parse_cell_reference(token), 1
        elif token.type == Dictionary.LEFT_PARENTHESES:
            # Find matching parenthesis to handle nested cases
            count = 1
            idx = 1
            while count > 0:
                if tokens[idx].type == Dictionary.LEFT_PARENTHESES:
                    count += 1
                elif tokens[idx].type == Dictionary.RIGHT_PARENTHESES:
                    count -= 1
                idx += 1
            # idx now is the position of the matching RIGHT_PARENTHESES
            node = self.parse_expression(tokens[1:idx-1])
            return node, idx  # return node and the index of the token after RIGHT_PARENTHESES
        else:
            raise ValueError(f"Unexpected token type {token.type}")

    def parse_if_statement(self, line):
        """Parse an if statement, assuming no block structure."""
        # Example parsing assuming format `if condition:`
        # if has already been parsed, next should be a single whitespace before the condition
        if line[1].type != Dictionary.WHITE_SPACE:
            raise ValueError("Expected whitespace after 'if'")
        # figure out which tokens are part of the left condition
        condition_identifiers = [Dictionary.EQUAL_TO, Dictionary.NOT_EQUAL_TO, Dictionary.GREATER_THAN, Dictionary.LESS_THAN, Dictionary.GREATER_THAN_OR_EQUAL_TO, Dictionary.LESS_THAN_OR_EQUAL_TO]
        condition = []
        i = 0
        # an if statement can be a single condition or a combination of conditions
        tokens = line[2:]
        # remove whitespace tokens
        tokens = [token for token in tokens if token.type != Dictionary.WHITE_SPACE]
        while True:
            condition_part = []
            i = 0
            # go until we get to the end of the tokens or find a equal to, not equal to, greater than, less than, greater than or equal to, or less than or equal to token
            while i < len(tokens) and tokens[i].type not in condition_identifiers:
                condition_part.append(tokens[i])
                i += 1
            condition.append(self.parse_expression(condition_part))
            if i == len(tokens):
                break
            condition.append(tokens[i].type)
            tokens = tokens[i+1:]
        # advanced the line count so we can parse the body
        self.current_line += 1
        body = []
        # for every line starts with a tab, parse it as a body
        while self.current_line < len(self.lines) and self.is_indented(self.lines[self.current_line]):
            # remove the identation token
            line = self.lines[self.current_line][1:]
            body.append(self.parse_line(line))
            self.current_line += 1
        # if the body is empty, raise an error
        if not body:
            raise ValueError(f"Expected body for if statement on line {self.current_line}")
            return None
        # todo: Maybe find a better way to do this.
        self.current_line -= 1 # get us to the previous line, because the outer loop will increment the line count
        return IfNode(condition, body)
    
    def parse_delete(self, line):
        """Parse an delete statement."""
        # remove whitespace tokens
        tokens = [token for token in line if token.type != Dictionary.WHITE_SPACE]
        # find the deletion token
        i = 0
        while tokens[i].value == 'delete':
            i += 1
        # everything before the assignment token is the variable
        # if there's more than 1 token before the assignment token, raise an error
        if i != 1:
            raise ValueError("Invalid assignment statement")
        variable = tokens[1]
        # if the variable is a cell reference, parse it
        if variable.type == Dictionary.CELL:
            variable = self.parse_cell_reference(variable)
        return DeleteNode(variable)

    def parse_assignment(self, line):
        """Parse an assignment statement."""
        # remove whitespace tokens
        tokens = [token for token in line if token.type != Dictionary.WHITE_SPACE]
        # find the assignment token
        i = 0
        while tokens[i].type != Dictionary.ASSIGNMENT:
            i += 1
        # everything before the assignment token is the variable
        # if there's more than 1 token before the assignment token, raise an error
        if i != 1:
            raise ValueError("Invalid assignment statement")
        variable = tokens[0]
        # if the variable is a cell reference, parse it
        print(variable.type)
        if variable.type == Dictionary.CELL:
            variable = self.parse_cell_reference(variable)
        # everything after the assignment token is the expression
        variable_value = tokens[i+1:]
        # if we only have 1 token, and it's an identifier, we can return the variable
        print(variable_value[0].type)
        if len(variable_value) == 1 and variable_value[0].type == Dictionary.IDENTIFIER:
            return AssignmentNode(variable, variable_value[0])
        # otherwise, parse the expression
        expression = self.parse_expression(variable_value)
        return AssignmentNode(variable, expression)
    
    def parse_cell_reference(self, token):
        """Parse a cell reference."""
        # token.value should be any amount of alphabetic characters followed by any amount of numeric characters
        # if there are no numeric characters, raise an error
        # if there are no alphabetic characters, raise an error
        # if there are any other characters, raise an error
        if not token.value:
            raise ValueError("Empty cell reference")
        if not any(char in token.value for char in Dictionary.NUMERIC_CHARACTERS):
            raise ValueError("Invalid cell reference")
        if not any(char in token.value for char in Dictionary.ALPHABETIC_CHARACTERS):
            raise ValueError("Invalid cell reference")
        if any(char not in Dictionary.NUMERIC_CHARACTERS | Dictionary.ALPHABETIC_CHARACTERS for char in token.value):
            raise ValueError("Invalid cell reference")
        # there can be no numeric characters before the alphabetic characters. SO go through the string until we find a numeric character, and then check if the rest of the string is numeric
        i = 0
        while i < len(token.value) and token.value[i] not in Dictionary.NUMERIC_CHARACTERS:
            i += 1
        if not token.value[i:].isnumeric():
            raise ValueError("Invalid cell reference")
        return CellReferenceNode(token.value)




    def is_indented(self, line):
        """Check if the line is indented (simple check based on first token being a whitespace or similar)."""
        return line[0].type == Dictionary.INDENTATION

    def parse(self):
        # Divide the tokens into lines
        self.lines = self._split_into_lines(self.tokens)
        ast = []
        while self.current_line < len(self.lines):
            #print(f"Current line: {self.current_line}")
            ast.append(self.parse_line(self.lines[self.current_line]))
            self.current_line += 1
            #print(f"AST: {ast}")
        return ast

