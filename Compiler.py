import sys

from sly import Lexer, Parser
# import LanguageLexer
from LanguageLexer import Lexer
from LanguageLexer import LanguageLexer

register_number = 1
variables = {}
arrays = {}
initialized_variables = set()
current_instruction = 0
temp_vars = set()


class Compiler(Parser):
    tokens = LanguageLexer.tokens

    def concat_commands(self, *instructions):
        instructions_with_counter = ('', 0)
        for tuples in instructions:
            instructions_with_counter = (
                instructions_with_counter[0] + tuples[0], instructions_with_counter[1] + tuples[1])
        return instructions_with_counter

    def verify_variable(self, identifier):
        if len(identifier) == 2 and identifier[1] not in variables:
            raise Exception("Variable not declared")
        elif len(identifier) == 5:
            if identifier[1] not in arrays:
                raise Exception("Array not declared")

    def load_constant_value(self, value):
        instructions_counter = 0
        current_instructions = '\nRESET a'
        for k in range(len(str(bin(abs(value)))[2:])):
            current_instructions += '\nSHL a'
            instructions_counter += 1
            if str(bin(abs(value)))[2:][k] == '1':
                instructions_counter += 1
                current_instructions += '\nINC a'
        return (current_instructions, instructions_counter + 1)

    def load_proper_cell_for_variable(self, identifier):
        if len(identifier) == 2:
            return self.load_constant_value(variables[identifier[1]])
        elif len(identifier) == 5:
            if type(identifier) == type(''):
                pass
            else:
                pass
        print(variables)
        print(arrays)
        print(identifier)

    def define_new_array(self, PIDENTIFIER, NUM0, NUM1):
        global register_number
        if NUM0 > NUM1:
            raise Exception('Error in array range: ' + PIDENTIFIER)
        if PIDENTIFIER in arrays:
            raise Exception("Duplicated array name: " + PIDENTIFIER)
        if PIDENTIFIER in variables:
            raise Exception("Duplicated variable name: " + PIDENTIFIER)
        else:
            arrays[PIDENTIFIER] = NUM0, NUM1, register_number
            register_number += NUM1 - NUM0 + 2

    def define_new_variable(self, PIDENTIFIER):
        global register_number
        if PIDENTIFIER in variables:
            raise Exception("Duplicated variable name at line: " + PIDENTIFIER)
        elif PIDENTIFIER in arrays:
            raise Exception("Duplicated array name at line: " + PIDENTIFIER)
        else:
            variables[PIDENTIFIER] = register_number
            register_number += 1

    def __init__(self):
        self.names = {}

    @_('DECLARE declarations BEGIN commands END')
    def empty(self, p):
        return p.commands[0] + '\nHALT'

    @_('BEGIN commands END')
    def empty(self, p):
        return p.commands[0] + '\nHALT'

    @_('declarations "," PIDENTIFIER')
    def declarations(self, p):
        self.define_new_variable(p.PIDENTIFIER)
        return p

    @_('declarations "," PIDENTIFIER "(" NUM ":" NUM ")"')
    def declarations(self, p):
        self.define_new_array(p.PIDENTIFIER, p.NUM0, p.NUM1)
        return p

    @_('PIDENTIFIER')
    def declarations(self, p):
        self.define_new_variable(p.PIDENTIFIER)
        return p

    @_('PIDENTIFIER "(" NUM ":" NUM ")"')
    def declarations(self, p):
        self.define_new_array(p.PIDENTIFIER, p.NUM0, p.NUM1)
        return p

    @_('commands command')
    def commands(self, p):
        return self.concat_commands(p.commands, p.command)

    @_('command')
    def commands(self, p):
        return p.command

    @_('identifier ASSIGN expression ";"')
    def command(self, p):
        self.verify_variable(p.identifier)
        STORE_AT_PROPER_CELL = self.load_proper_cell_for_variable(p.identifier)
        return self.concat_commands(p.expression, ('\nRESET b\nADD b a', 2), STORE_AT_PROPER_CELL, ('\nSTORE b a', 1))

    @_('IF condition THEN commands ELSE commands ENDIF')
    def command(self, p):
        return self.concat_commands(p.condition, (f'\nJZERO a 2\nJUMP {2 + p.commands0[1]}', 2), p.commands0,
                                    (f'\nJUMP {p.commands1[1] + 1}', 1), p.commands1)

    @_('IF condition THEN commands ENDIF')
    def command(self, p):
        return p

    @_('WHILE condition DO commands ENDWHILE')
    def command(self, p):
        return p

    @_('REPEAT commands UNTIL condition ";"')
    def command(self, p):
        return p

    @_('FOR PIDENTIFIER FROM value TO value DO commands ENDFOR')
    def command(self, p):
        return p

    @_('FOR PIDENTIFIER FROM value DOWNTO value DO commands ENDFOR')
    def command(self, p):
        return p

    @_('READ identifier ";"')
    def command(self, p):
        LOAD_CELL_NUMBER = self.load_proper_cell_for_variable(p.identifier)
        return self.concat_commands(LOAD_CELL_NUMBER, ('\nGET a ', 1))

    @_('WRITE value ";"')
    def command(self, p):
        return self.concat_commands(p.value, ('\nRESET b\nSTORE a b\nPUT b', 3))

    @_('value')
    def expression(self, p):
        return p.value

    @_('value "+" value')
    def expression(self, p):
        STORE_TEMPORARLY_AT_B = '\nRESET b\nADD b a', 2
        return self.concat_commands(p.value0, STORE_TEMPORARLY_AT_B, p.value1, ('\nADD a b', 1))

    @_('value "-" value')
    def expression(self, p):
        STORE_TEMPORARLY_AT_B = '\nRESET b\nADD b a', 2
        return self.concat_commands(p.value1, STORE_TEMPORARLY_AT_B, p.value0, ('\nSUB a b', 1))

    @_('value "*" value')
    def expression(self, p):
        return p

    @_('value "/" value')
    def expression(self, p):
        return p

    @_('value "%" value')
    def expression(self, p):
        return p

    @_('value "=" value')
    def condition(self, p):
        STORE_TEMPORARLY_AT_B_AND_C = '\nRESET b\nADD b a\nRESET c\nADD c a', 4
        return self.concat_commands(p.value1, STORE_TEMPORARLY_AT_B_AND_C, p.value0,
                                    ('\nSUB b a\nJZERO b 2\nJUMP 3\nSUB a c\nJZERO a 2\nINC a', 6))

    @_('value NEQ value')
    def condition(self, p):
        STORE_TEMPORARLY_AT_B_AND_C = '\nRESET b\nADD b a\nRESET c\nADD c a', 4
        return self.concat_commands(p.value1, STORE_TEMPORARLY_AT_B_AND_C, p.value0, (
            '\nSUB b a\nSUB a c\nJZERO a 2\nJUMP 2\nJZERO b 3\nRESET a\nJUMP 2\nINC a', 8))

    @_('value LE value')
    def condition(self, p):
        STORE_TEMPORARLY_AT_B = '\nRESET b\nADD b a', 2
        return self.concat_commands(p.value1, STORE_TEMPORARLY_AT_B, p.value0, ('\nINC a\nSUB a b', 2))

    @_('value GE value')
    def condition(self, p):
        STORE_TEMPORARLY_AT_B = '\nRESET b\nADD b a', 2
        return self.concat_commands(p.value0, STORE_TEMPORARLY_AT_B, p.value1, ('\nINC a\nSUB a b', 2))

    @_('value LEQ value')
    def condition(self, p):
        STORE_TEMPORARLY_AT_B = '\nRESET b\nADD b a', 2
        return self.concat_commands(p.value1, STORE_TEMPORARLY_AT_B, p.value0, ('\nSUB a b', 1))

    @_('value GEQ value')
    def condition(self, p):
        STORE_TEMPORARLY_AT_B = '\nRESET b\nADD b a', 2
        return self.concat_commands(p.value0, STORE_TEMPORARLY_AT_B, p.value1, ('\nSUB a b', 1))

    @_('NUM')
    def value(self, p):
        return self.load_constant_value(p.NUM)

    @_('identifier')
    def value(self, p):
        LOAD_CELL_NUMBER = self.load_proper_cell_for_variable(p.identifier)
        return self.concat_commands(LOAD_CELL_NUMBER, ('\nLOAD a a', 1))

    @_('PIDENTIFIER')
    def identifier(self, p):
        return p

    @_('PIDENTIFIER "(" PIDENTIFIER ")"')
    def identifier(self, p):
        return p

    @_('PIDENTIFIER "(" NUM ")"')
    def identifier(self, p):
        return p


########################################################################################################################
def debug():
    for tok in lexer.tokenize(open(sys.argv[1], "r").read()):
        print('type=%r, value=%r' % (tok.type, tok.value))


if __name__ == '__main__':
    lexer = LanguageLexer()
    parser = Compiler()
    # debug()

    output = parser.parse(lexer.tokenize(open(sys.argv[1], "r").read())).split('\n', 1)[1]

    print(variables)
    print(arrays)

    fw = open(sys.argv[2], "w")
    fw.write(output)
