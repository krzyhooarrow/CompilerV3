from sly import Lexer


class LanguageLexer(Lexer):
    tokens = {DECLARE, BEGIN, END,
              NUM,
              TIMES, PLUS, MINUS, DIV, MOD,
              NEQ, LEQ, GEQ, LE, GE,
              ASSIGN,
              IF, THEN, ELSE, ENDIF,
              WHILE, ENDWHILE, DO,
              REPEAT, UNTIL, FOR, FROM, TO, DOWNTO, ENDFOR,
              READ, WRITE,
              PIDENTIFIER
              }

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

    @_(r'\n+')
    def ignore_newline(self, t):
        self.lineno += len(t.value)

    @_(r'\t+')
    def ignore_tabs(self, t):
        self.lineno += len(t.value)

    @_(r' ')
    def ignore_spaces(self, t):
        self.lineno += len(t.value)

    @_(r'\[[^\]]*\]')
    def ignore_comments(self, t):
        self.lineno += len(t.value)

    @_(r'[0-9]+')
    def NUM(self, t):
        t.value = int(t.value)  # Convert to a numeric value
        return t

    def error(self, t):
        print("Illegal character '%s'" % t.value[0])
        self.index += 1
