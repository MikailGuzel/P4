from Token import Token

class Dictionary:
    NUMERIC_CHARACTERS  = set('0123456789.')
    ALPHABETIC_CHARACTERS = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')
    KEYWORDS = ['if', 'else if', 'else', 'return', 'delete']

    # TOKEN TYPES
    INTEGER                     = 'INT'
    FLOAT                       = 'FLOAT'
    CELL                        = 'CELL'
    PLUS                        = 'PLUS'
    STRING                      = 'STR'
    MINUS                       = 'MINUS'
    MULTIPLICATION              = 'MULT'
    DIVISION                    = 'DIV'
    LEFT_PARENTHESES            = 'L_PRNTH'
    RIGHT_PARENTHESES           = 'R_PRNTH'
    NEWLINE                     = 'NL'
    INDENTATION                 = 'TAB'
    WHITE_SPACE                 = 'WS'
    KEYWORD                     = 'KW'
    IDENTIFIER                  = 'ID'
    ASSIGNMENT                  = 'ASSIGN'
    DELETE                      = 'DELETE'
    EQUAL_TO                    = '=='
    NOT_EQUAL_TO                = '!='
    GREATER_THAN                = '>'
    LESS_THAN                   = '<'
    GREATER_THAN_OR_EQUAL_TO    = '>='
    LESS_THAN_OR_EQUAL_TO       = '<='

    multi_word_operator_parts = ['is', 'not', 'equal', 'to', 'greater', 'or', 'less', 'than']
    
    multi_word_operators = {
        'is equal to': EQUAL_TO,
        'is not equal to': NOT_EQUAL_TO,
        'is greater than': GREATER_THAN,
        'is less than': LESS_THAN,
        'is greater than or equal to': GREATER_THAN_OR_EQUAL_TO,
        'is less than or equal to': LESS_THAN_OR_EQUAL_TO
    }

    arithmetic_operators = {
        '+': Token(PLUS),
        '-': Token(MINUS),
        '*': Token(MULTIPLICATION),
        '/': Token(DIVISION),
        '(': Token(LEFT_PARENTHESES),
        ')': Token(RIGHT_PARENTHESES),
        '=': Token(ASSIGNMENT),
        'is': Token(ASSIGNMENT)
    }

    multi_word_operators_dictionary = {
        'is equal to': Token(EQUAL_TO),
        'is not equal to': Token(NOT_EQUAL_TO),
        'is greater than': Token(GREATER_THAN),
        'is less than': Token(LESS_THAN),
        'is greater than or equal to': Token(GREATER_THAN_OR_EQUAL_TO),
        'is less than or equal to': Token(LESS_THAN_OR_EQUAL_TO)
    }

    escape_characters = {
        '\n': Token(NEWLINE),
        '\t': Token(INDENTATION),
        ' ' : Token(WHITE_SPACE)
    }
