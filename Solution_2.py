class SyntaxErr(Exception):
    pass


ID, NUM, NOT, AND, OR, XOR, ASSIGN, LP, RP, SEMI, EOF = (
    "ID", "NUM", "~", "&", "|", "^", "=", "(", ")", ";", "$"
)

SYMBOLS = {
    "~": NOT, "&": AND, "|": OR, "^": XOR,
    "=": ASSIGN, "(": LP, ")": RP, ";": SEMI,
}


def is_letter(c):
    return ("a" <= c <= "z") or ("A" <= c <= "Z")


def is_digit(c):
    return "0" <= c <= "9"


def ok_digit(base, c):
    return c in "01" if base == "b" else c in "012"


def lex(s):
    toks = []
    i, n = 0, len(s)
    while i < n:
        c = s[i]
        if c.isspace():
            i += 1
            continue

        if is_letter(c):
            j = i + 1
            if j < n and (is_letter(s[j]) or is_digit(s[j])):
                j += 1
            toks.append(ID)
            i = j
            continue

        if is_digit(c):
            j = i + 1
            if c == "0" and j < n and s[j] in "bt":
                base = s[j]
                k = j + 1
                while k < n and ok_digit(base, s[k]):
                    k += 1
                if k > j + 1:
                    toks.append(NUM)
                    i = k
                    continue
            while j < n and is_digit(s[j]):
                j += 1
            toks.append(NUM)
            i = j
            continue

        if c in SYMBOLS:
            toks.append(SYMBOLS[c])
            i += 1
            continue

        raise SyntaxErr()

    toks.append(EOF)
    return toks


class Parser:
    def __init__(self, src):
        self.toks = lex(src)
        self.pos = 0

    def peek(self):
        return self.toks[self.pos]

    def next(self):
        self.pos += 1

    def expect(self, t):
        if self.peek() != t:
            raise SyntaxErr()
        self.pos += 1

    def first_s(self):
        return self.peek() in (ID, NOT, NUM, LP)

    def P(self):
        self.S()
        self.R()
        self.expect(EOF)

    def R(self):
        if self.peek() == SEMI:
            self.next()
            self.O()

    def O(self):
        if self.first_s():
            self.S()
            self.R()

    def S(self):
        t = self.peek()
        if t == ID:
            self.next()
            self.T()
        elif t in (NOT, NUM, LP):
            self.N()
            self.M()
            self.A()
        else:
            raise SyntaxErr()

    def T(self):
        if self.peek() == ASSIGN:
            self.next()
            self.S()
        else:
            self.M()
            self.A()

    def N(self):
        t = self.peek()
        if t == NOT:
            self.next()
            self.V()
        elif t == NUM:
            self.next()
        elif t == LP:
            self.next()
            self.S()
            self.expect(RP)
        else:
            raise SyntaxErr()

    def U(self):
        self.V()
        self.M()

    def M(self):
        if self.peek() == AND:
            self.next()
            self.V()
            self.M()

    def A(self):
        if self.peek() in (OR, XOR):
            self.next()
            self.U()
            self.A()


    def V(self):
        if self.peek() == NOT:
            self.next()
            self.V()
        else:
            self.F()

    def F(self):
        t = self.peek()
        if t in (ID, NUM):
            self.next()
        elif t == LP:
            self.next()
            self.S()
            self.expect(RP)
        else:
            raise SyntaxErr()


def accepts(src):
    try:
        Parser(src).P()
        return True
    except SyntaxErr:
        return False


tests = [
    ("a = b = 0b101 & ~c | 12;", True),
    ("(x1 ^ 0t12) & y; z = (y = 1);", True),
    ("~~a | b & c ^ 7", True),
    ("a = 5;", True),
    ("a | b = 3", False),
    ("(a) = 1", False),
    ("a = ;", False),
    ("0b102", False),
    ("abc = 1", False),
    ("a && b", False),
    ("", False),
]
for src, expected in tests:
    got = accepts(src)
    print("OK  " if got == expected else "FAIL", repr(src), "->",
            "Accepted" if got else "Rejected")