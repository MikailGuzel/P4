import logging

from Token import Token
from dictionary import Dictionary

logger = logging.getLogger(__name__)

class CodeGenerator:
    def __init__(self, ast):
        self.ast = ast

    def generate(self, node=None, is_root=True):
        if not is_root:
            logger.debug(f'Generating code for {type(node).__name__}')
            print(node)
            method_name = 'generate_' + type(node).__name__
            generate_method = getattr(self, method_name, self.generic_generate)
            return generate_method(node)
        
        if is_root:  # Check if this is the root call
            code = ""
            for node in self.ast:
                code += f"{self.generate(node, is_root=False)}\n"
            header = self.generate_header()
            footer = self.generate_footer()
            code = f"{header}\n{code}\n{footer}"
            return code

    def generic_generate(self, node):
        logger.error(f'No code generation method defined for {type(node).__name__}')
        return None

    def generate_header(self):
        return """
import sys
from openpyxl import load_workbook

if len(sys.argv) < 2:
    print(f"Usage: python {sys.argv[0]} <excel_file>")
    sys.exit(1)

workbook = load_workbook(filename=sys.argv[1])
sheet = workbook.active
"""

    def generate_footer(self):
        return """
workbook.save(filename=sys.argv[1])
"""

    # Node-specific generation methods follow...
    def generate_NumberNode(self, node):
        return str(node.value)

    def generate_StringNode(self, node):
        return str(node.value)

    def generate_ExpressionNode(self, node):
        left_code = self.generate(node.left, is_root=False)
        right_code = self.generate(node.right, is_root=False)
        if node.operator == Dictionary.PLUS:
            operator = '+'
        elif node.operator == Dictionary.MINUS:
            operator = '-'
        elif node.operator == Dictionary.MULTIPLICATION:
            operator = '*'
        elif node.operator == Dictionary.DIVISION:
            operator = '/'
        else:
            logger.error(f'Unsupported operator {node.operator}')
            return None
        return f'({left_code} {operator} {right_code})'
    
    def generate_IfNode(self, node):
            condition_code = ''
            for condition in node.condition:
                if isinstance(condition, str):
                    condition_code += condition
                else:
                    condition_code += self.generate(condition, is_root=False)
            body_code = ''
            for body in node.body:
                body_code += f"    {self.generate(body, is_root=False)}\n"
            return f'if {condition_code}:\n{body_code}'

    def generate_DeleteNode(self, node):
        if not isinstance(node.identifier, Token):
            identifier_code = self.generate(node.identifier, is_root=False)
        else:
            identifier_code = node.identifier.value
        return f"{identifier_code} = None"

    def generate_AssignmentNode(self, node):
        if not isinstance(node.identifier, Token):
            identifier_code = self.generate(node.identifier, is_root=False)
        else:
            identifier_code = node.identifier.value
        if not isinstance(node.value, Token):
            value_code = self.generate(node.value, is_root=False)
        else:
            value_code = node.value.value
        return f"{identifier_code} = {value_code}"
    
    def generate_IdentifierNode(self, node):
        return node.value
    
    def generate_CellReferenceNode(self, node):
        return f"sheet['{node.value}'].value"
    


