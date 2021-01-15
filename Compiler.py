import sys

from sly import Parser
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

    def verify_initialization(self, identifier):
        if len(identifier) == 2 and identifier[1] not in initialized_variables:
            raise Exception("Variable not initialized: " + str(identifier))
        # elif len(identifier) == 5:
        #     if identifier[1] not in arrays:
        #         raise Exception("Array not declared")

    def verify_declaration(self, identifier):
        if len(identifier) == 2 and identifier[1] not in variables:
            raise Exception("Variable not declared")

    def initialize_variable(self, identifier):
        initialized_variables.add(identifier[1])

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
            if type(identifier[3]) == type(''):
                array = arrays[identifier[1]]
                load_variable = self.concat_commands(self.load_constant_value(variables[identifier[3]]), ('\nLOAD b a', 1))
                if array[0] > array[2]:
                    return self.concat_commands(load_variable, self.load_constant_value(array[0] - array[2]), ('\nSUB b a\nRESET a\nADD a b', 3))
                else:
                    return self.concat_commands(load_variable, self.load_constant_value(array[2] - array[0]), ('\nADD a b', 1))
            else:
                return self.load_constant_value(identifier[3] - arrays[identifier[1]][0] + arrays[identifier[1]][2])

    def create_temporary_variable(self):
        global register_number
        self.define_new_variable(f'TEMPORARY_VARIABLE_{register_number}')
        return ('value', f'TEMPORARY_VARIABLE_{register_number - 1}')

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

    def remove_temporary_variables(self, *PIDENTIFIER):
        for id in PIDENTIFIER:
            variables.pop(id[1])
            # initialized_variables.remove(id[1])
            # temp_vars.remove(id[1])

    def substitute_and_store_loop_values(self, value1, value2, LOOP_ITERATOR, increment):
        if increment:
            LOAD_FIRST_VALUE_AND_STORE_AS_FIRST_ITERATOR_VALUE = self.concat_commands(value1, ('\nRESET f\nADD f a', 2), self.load_proper_cell_for_variable(LOOP_ITERATOR), ('\nSTORE f a', 1))
            LOOP_ITERATIONS_COUNTER = self.create_temporary_variable()
            STORE_ITERATIONS_COUNTER = self.concat_commands(LOAD_FIRST_VALUE_AND_STORE_AS_FIRST_ITERATOR_VALUE, value2, ('\nINC a\nSUB a f\nRESET f\nADD f a', 4), self.load_proper_cell_for_variable(LOOP_ITERATIONS_COUNTER), ('\nSTORE f a', 1))
        else:
            LOAD_FIRST_VALUE_AND_STORE_AS_FIRST_ITERATOR_VALUE = self.concat_commands(value1, ('\nRESET f\nADD f a', 2), self.load_proper_cell_for_variable(LOOP_ITERATOR), ('\nSTORE f a', 1))
            LOOP_ITERATIONS_COUNTER = self.create_temporary_variable()
            STORE_ITERATIONS_COUNTER = self.concat_commands(LOAD_FIRST_VALUE_AND_STORE_AS_FIRST_ITERATOR_VALUE, value2, ('\nINC f\nSUB f a', 2), self.load_proper_cell_for_variable(LOOP_ITERATIONS_COUNTER), ('\nSTORE f a', 1))

        return (STORE_ITERATIONS_COUNTER, LOOP_ITERATOR, LOOP_ITERATIONS_COUNTER)

    def load_variable_increment_or_decrement_and_save(self, variable, increment):
        INC_OR_DEC = 'INC b' if increment else 'DEC b'
        return self.concat_commands(self.load_proper_cell_for_variable(variable), (f'\nLOAD b a\n{INC_OR_DEC}\nSTORE b a', 3))

    def verify_iterator_increment_and_save(self, LOOP_ITERATOR, LOOP_ITERATIONS_COUNTER, increment):
        UPDATE_ITERATOR = self.load_variable_increment_or_decrement_and_save(LOOP_ITERATOR, increment)
        LOAD_ITERATIONS_COUNTER = self.concat_commands(self.load_proper_cell_for_variable(LOOP_ITERATIONS_COUNTER), ('\nLOAD b a\nJZERO b 5\nDEC b\nSTORE b a\nRESET a', 5))
        return self.concat_commands(UPDATE_ITERATOR, LOAD_ITERATIONS_COUNTER)

    def loop(self, p, IS_UPTO_TYPE):
        STORE_ITERATOR_COMMANDS, LOOP_ITERATOR, LOOP_ITERATIONS_COUNTER = self.substitute_and_store_loop_values(p.value0, p.value1, p.iterator, IS_UPTO_TYPE)
        LOAD_ITERATOR_INCREMENT_AND_SAVE = self.verify_iterator_increment_and_save(LOOP_ITERATOR, LOOP_ITERATIONS_COUNTER, IS_UPTO_TYPE)
        VERIFY_LOOP_CONDITION = self.concat_commands(self.load_proper_cell_for_variable(LOOP_ITERATIONS_COUNTER), (f'\nLOAD b a\nJZERO b {2 + p.commands[1] + LOAD_ITERATOR_INCREMENT_AND_SAVE[1]}', 2))
        self.remove_temporary_variables(LOOP_ITERATOR, LOOP_ITERATIONS_COUNTER)
        return self.concat_commands(STORE_ITERATOR_COMMANDS, VERIFY_LOOP_CONDITION, p.commands, LOAD_ITERATOR_INCREMENT_AND_SAVE, (f'\nJZERO a -{1 + LOAD_ITERATOR_INCREMENT_AND_SAVE[1] + p.commands[1]}', 1))

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
        self.initialize_variable(p.identifier)
        return self.concat_commands(p.expression, ('\nRESET f\nADD f a', 2), self.load_proper_cell_for_variable(p.identifier), ('\nSTORE f a', 1))

    @_('IF condition THEN commands ELSE commands ENDIF')
    def command(self, p):
        return self.concat_commands(p.condition, (f'\nJZERO a 2\nJUMP {2 + p.commands0[1]}', 2), p.commands0, (f'\nJUMP {p.commands1[1] + 1}', 1), p.commands1)

    @_('IF condition THEN commands ENDIF')
    def command(self, p):
        return self.concat_commands(p.condition, (f'\nJZERO a 2\nJUMP {1 + p.commands[1]}', 2), p.commands)

    @_('WHILE condition DO commands ENDWHILE')
    def command(self, p):
        return self.concat_commands(p.condition, (f'\nJZERO a 2\nJUMP {2 + p.commands[1]}', 2), p.commands, (f'\nJUMP -{2 + p.commands[1] + p.condition[1]}', 1))

    @_('REPEAT commands UNTIL condition ";"')
    def command(self, p):
        return self.concat_commands(p.commands, p.condition, (f'\nJZERO a 2\nJUMP -{1 + p.commands[1] + p.condition[1]}', 2))

    @_('FOR iterator FROM value TO value DO commands ENDFOR')
    def command(self, p):
        return self.loop(p, True)

    @_('FOR iterator FROM value DOWNTO value DO commands ENDFOR')
    def command(self, p):
        return self.loop(p, False)

    @_('PIDENTIFIER')
    def iterator(self, p):
        self.initialize_variable(('identifier',p.PIDENTIFIER))
        self.define_new_variable(p.PIDENTIFIER)
        return ('value', p.PIDENTIFIER)

    @_('READ identifier ";"')
    def command(self, p):
        self.verify_declaration(p.identifier)
        self.initialize_variable(p.identifier)
        return self.concat_commands(self.load_proper_cell_for_variable(p.identifier), ('\nGET a ', 1))

    @_('WRITE value ";"')
    def command(self, p):
        return self.concat_commands(p.value, ('\nRESET b\nSTORE a b\nPUT b', 3))

    @_('value')
    def expression(self, p):
        return p.value

    @_('value PLUS value')
    def expression(self, p):
        return self.concat_commands(p.value0, ('\nRESET f\nADD f a', 2), p.value1, ('\nADD a f', 1))

    @_('value MINUS value')
    def expression(self, p):
        return self.concat_commands(p.value1, ('\nRESET f\nADD f a', 2), p.value0, ('\nSUB a f', 1))

    @_('value TIMES value')
    def expression(self, p):
        return self.concat_commands(p.value0, (f'\nRESET c\nADD c a\nJZERO a {14 + p.value1[1]}', 3), p.value1, (f'\nRESET d\nRESET b\nADD d a\nJZERO a 10\nJODD c 2\nJUMP 2\nADD b a\nSHL a\nSHR c\nJZERO c 2\nJUMP -6\nRESET a\nADD a b', 13))

    @_('value DIV value')
    def expression(self, p):
        STORE_VALUES = self.concat_commands(p.value1, (f'\nRESET c\nADD c a\nRESET d\nADD d a\nJZERO a {30 + p.value0[1]}', 5), p.value0, ('\nRESET b\nADD b a\nRESET e\nRESET f\nINC e', 5))
        DIVIDE = ('\nSUB a c\nJZERO a 5\nADD a c\nSHL c\nSHL e\nJUMP -5\nJODD e 12\nSHR c\nSUB b c\nRESET a\nADD a b\nRESET c\nADD c d\nSHR e\nADD f e\nRESET e\nINC e\nJUMP -17', 18)
        RETURN_PARTIAL_SUM = ('\nSUB d b\nJZERO d 2\nJUMP 2\nINC f\nRESET a\nADD a f', 6)
        return self.concat_commands(STORE_VALUES, DIVIDE, RETURN_PARTIAL_SUM)

    @_('value MOD value')
    def expression(self, p):
        STORE_VALUES = self.concat_commands(p.value1, (f'\nRESET c\nADD c a\nRESET f\nRESET d\nRESET e\nADD e a\nJZERO a {26 + p.value0[1] + p.value1[1]}', 7), p.value0, ('\nADD d a', 1))
        REMOVE_FROM_HIGHEST_POWER_TO_LOWEST = ('\nSUB a c\nJZERO a 5\nADD a c\nSHL c\nINC f\nJUMP -5\nADD a d\nJZERO f 8\nSHR c\nSUB a c\nSUB d c\nRESET c\nADD c e\nRESET f\nJUMP -14', 15)
        RETURN_VALUE = self.concat_commands(('\nRESET c\nADD c a\nRESET d\nADD d a', 4), p.value1, ('\nINC c\nSUB c a\nRESET a\nJODD c 2\nADD a d', 5))
        return self.concat_commands(STORE_VALUES, REMOVE_FROM_HIGHEST_POWER_TO_LOWEST, RETURN_VALUE)

    @_('value "=" value')
    def condition(self, p):
        return self.concat_commands(p.value1, ('\nRESET d\nADD d a\nRESET c\nADD c a', 4), p.value0, ('\nSUB d a\nJZERO d 2\nJUMP 3\nSUB a c\nJZERO a 2\nINC a', 6))

    @_('value NEQ value')
    def condition(self, p):
        return self.concat_commands(p.value1, ('\nRESET d\nADD d a\nRESET c\nADD c a', 4), p.value0, ('\nSUB d a\nSUB a c\nJZERO a 2\nJUMP 2\nJZERO d 3\nRESET a\nJUMP 2\nINC a', 8))

    @_('value LE value')
    def condition(self, p):
        return self.concat_commands(p.value1, ('\nRESET d\nADD d a', 2), p.value0, ('\nINC a\nSUB a d', 2))

    @_('value GE value')
    def condition(self, p):
        return self.concat_commands(p.value0, ('\nRESET d\nADD d a', 2), p.value1, ('\nINC a\nSUB a d', 2))

    @_('value LEQ value')
    def condition(self, p):
        return self.concat_commands(p.value1, ('\nRESET d\nADD d a', 2), p.value0, ('\nSUB a d', 1))

    @_('value GEQ value')
    def condition(self, p):
        return self.concat_commands(p.value0, ('\nRESET d\nADD d a', 2), p.value1, ('\nSUB a d', 1))

    @_('NUM')
    def value(self, p):
        return self.load_constant_value(p.NUM)

    @_('identifier')
    def value(self, p):
        self.verify_initialization(p.identifier)
        return self.concat_commands(self.load_proper_cell_for_variable(p.identifier), ('\nLOAD a a', 1))

    @_('PIDENTIFIER')
    def identifier(self, p):
        return p

    @_('PIDENTIFIER "(" PIDENTIFIER ")"')
    def identifier(self, p):
        self.verify_initialization(('identifier', p.PIDENTIFIER1))
        return p

    @_('PIDENTIFIER "(" NUM ")"')
    def identifier(self, p):
        return p


########################################################################################################################
# def debug():
#     for tok in lexer.tokenize(open(sys.argv[1], "r").read()):
#         print('type=%r, value=%r' % (tok.type, tok.value))

if __name__ == '__main__':
    # try:
    lexer = LanguageLexer()
    parser = Compiler()
    output = parser.parse(lexer.tokenize(open(sys.argv[1], "r").read())).split('\n', 1)[1]
    print(variables)
    print(arrays)
    fw = open(sys.argv[2], "w")
    fw.write(output)
# except:
#     raise Exception("An exception occurred during parsing")
