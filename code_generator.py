import logging

from dictionary import Dictionary

logger = logging.getLogger(__name__)

class CodeGenerator:
    def __init__(self, ast):
        self.ast = ast

    def generate(self, node=None, is_root=True):
        if not is_root:
            logger.debug(f'Generating code for {type(node).__name__}')
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
        print(node)
        return None

    def generate_header(self):
        return """
import sys
from openpyxl import load_workbook

if len(sys.argv) < 2:
    print(f"Usage: python {sys.argv[1]} <excel_file>")
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

    def generate_ExpressionNode(self, node):
        left_code = self.generate(node.left, is_root=False)
        print(left_code)
        right_code = self.generate(node.right, is_root=False)
        print(right_code)
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
        print(f'({left_code} {operator} {right_code})')
        return f'({left_code} {operator} {right_code})'
    
    def generate_IfNode(self, node):
            condition_code = ''
            for condition in node.condition:
                if isinstance(condition, str):
                    condition_code += condition
                else:
                    condition_code += self.generate(condition[0], is_root=False)
            print(condition_code)
            body_code = ''
            for body in node.body:
                body_code += f"    {self.generate(body, is_root=False)}\n"
            return f'if {condition_code}:\n{body_code}'

    def generate_AssignmentNode(self, node):
        code = f"{node.identifier.value} = "
        if node.value.type == Dictionary.IDENTIFIER:
            code += f"{node.value.value}"
        else:
            code += f"{self.generate(node.value, is_root=False)}"
        return code
    
    def generate_IdentifierNode(self, node):
        return node.value
    


