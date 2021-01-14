from sly import Lexer


class LanguageLexer(Lexer):
    tokens = {DECLARE, BEGIN, END,
              # SEMICOLON, COMMA,
              # TIMES,

              NUM,
              TIMES, PLUS, MINUS, DIV, MOD,

              NEQ, LEQ, GEQ, LE, GE,
              ASSIGN,
              # LEFT_BRACKET, RIGHT_BRACKET, COLON,
              IF, THEN, ELSE, ENDIF,
              WHILE, ENDWHILE, DO,
              REPEAT, UNTIL, FOR, FROM, TO, DOWNTO, ENDFOR,
              READ, WRITE,
              PIDENTIFIER
              }

    ##### ODPOWIEDNIO USTAWIC ENDIFY NA ODP WYSOKOSCI ITP
    # TIMES = r'\*'
    literals = {';', ',', '(', ')', '+', '-', '/', '%', '=', ':'}

    DECLARE = r'DECLARE'
    BEGIN = r'BEGIN'

    PLUS = r'\+'
    MINUS = r'-'
    TIMES = r'\*'
    DIV = r'/'
    MOD = r'%'

    ASSIGN = r':='
    LEQ = r'<='
    GEQ = r'>='
    LE = r'<'
    GE = r'>'
    NEQ = r'!='

    IF = r'IF'
    THEN = r'THEN'
    ELSE = r'ELSE'
    ENDIF = r'ENDIF'

    DOWNTO = r'DOWNTO'
    DO = r'DO'
    FOR = r'FOR'
    FROM = r'FROM'
    TO = r'TO'
    ENDFOR = r'ENDFOR'

    REPEAT = r'REPEAT'
    UNTIL = r'UNTIL'
    WHILE = r'WHILE'
    ENDWHILE = r'ENDWHILE'
    READ = r'READ'
    WRITE = r'WRITE'

    END = r'END'
    PIDENTIFIER = r'[_a-z]+'

    # PIDENTIFIER['DECLARE'] = DECLARE
    # PIDENTIFIER['BEGIN'] = BEGIN
    # PIDENTIFIER['IF'] = IF
    # PIDENTIFIER['THEN'] = THEN
    # PIDENTIFIER['ELSE'] = ELSE
    # PIDENTIFIER['ENDIF'] = ENDIF
    # PIDENTIFIER['END'] = END

    ignore = " \t\n"

    @_(r'[0-9]+')
    def NUM(self, t):
        t.value = int(t.value)  # Convert to a numeric value
        return t

    def error(self, t):
        print("Illegal character '%s'" % t.value[0])
        self.index += 1
