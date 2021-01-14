from sly import Lexer, Parser


class LanguageLexer(Lexer):
    # tokens = { NAME, NUMBER, PLUS, TIMES, MINUS, DIVIDE, ASSIGN, LPAREN, RPAREN }
    tokens = {DECLARE, BEGIN, END,
              # SEMICOLON, COMMA,
              NUM,
              # PLUS, MINUS, TIMES, DIV, MOD,
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

    literals = {';', ',', '(', ')', '+', '-', '*', '/', '%', '=', ':'}

    DECLARE = r'DECLARE'
    BEGIN = r'BEGIN'

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

    DO = r'DO'
    FOR = r'FOR'
    FROM = r'FROM'
    TO = r'TO'
    DOWNTO = r'DOWNTO'
    ENDFOR = r'ENDFOR'

    REPEAT = r'REPEAT'
    UNTIL = r'UNTIL'
    WHILE = r'WHILE'
    ENDWHILE = r'ENDWHILE'
    READ = r'READ'
    WRITE = r'WRITE'

    END = r'END'
    PIDENTIFIER = r'[_a-z]+'

    PIDENTIFIER['DECLARE'] = DECLARE
    PIDENTIFIER['BEGIN'] = BEGIN
    PIDENTIFIER['IF'] = IF
    PIDENTIFIER['THEN'] = THEN
    PIDENTIFIER['ELSE'] = ELSE
    PIDENTIFIER['ENDIF'] = ENDIF
    PIDENTIFIER['END'] = END

    ignore = "[ \t\n]*"

    @_(r'\d+')
    def NUM(self, t):
        t.value = int(t.value)  # Convert to a numeric value
        return t

    def error(self, t):
        print("Illegal character '%s'" % t.value[0])
        self.index += 1
