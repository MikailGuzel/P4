import logging

from Dictionary import Dictionary
from parser_nodes import NumberNode, BinaryOperationNode

logger = logging.getLogger(__name__)

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens # the tokens we got from the lexer
        self.current_index = 0

    def peek(self):
        if self.current_index < len(self.tokens):
            return self.tokens[self.current_index]
        return None

    def consume(self, expected_type=None):
        current_token = self.peek()
        if expected_type and (current_token is None or current_token.type != expected_type):
            raise Exception(f"Expected token type {expected_type} but got {current_token.type if current_token else 'None'}")
        self.current_index += 1
        return current_token

    def parse(self):
        return self.expression()

    def expression(self):
        # Start with the lower precedence operation
        node = self.term()
        while self.peek() and self.peek().type in ['PLUS', 'MINUS']:
            op_token = self.consume()
            right = self.term()
            node = BinaryOperationNode(left=node, operator=op_token.type, right=right)
        return node

    def term(self):
        # Handles multiplication and division with higher precedence
        node = self.factor()
        while self.peek() and self.peek().type in ['MULT', 'DIV']:
            op_token = self.consume()
            right = self.factor()
            node = BinaryOperationNode(left=node, operator=op_token.type, right=right)
        return node

    def factor(self):
        # Number or parenthesized expression
        token = self.peek()
        if token.type in [Dictionary.INTEGER, Dictionary.FLOAT]:
            self.consume()
            return NumberNode(token.value)
        elif token.type == Dictionary.LEFT_PARENTHESES:
            self.consume(Dictionary.LEFT_PARENTHESES)
            node = self.expression()
            self.consume(Dictionary.RIGHT_PARENTHESES)
            return node
        else:
            raise Exception(f"Unexpected token {token.type}")
