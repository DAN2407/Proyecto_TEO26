"""Analizador léxico para un subconjunto de C."""
from dataclasses import dataclass
import re

KEYWORDS = {"int", "if", "else", "while"}

# Orden importa: operadores de 2 caracteres antes que los de 1.
TOKEN_SPEC = [
    ("WS",     r"[ \t\r]+"),
    ("NL",     r"\n"),
    ("COMENT", r"//[^\n]*"),
    ("NUM",    r"\d+"),
    ("ID",     r"[A-Za-z_]\w*"),
    ("OP2",    r"==|!=|<=|>=|&&|\|\|"),
    ("OP1",    r"[+\-*/%<>=!]"),
    ("PUNT",   r"[(){};]"),
    ("ERROR",  r"."),
]
MASTER = re.compile("|".join(f"(?P<{n}>{p})" for n, p in TOKEN_SPEC))


@dataclass
class Token:
    tipo: str      # 'NUM', 'ID', 'EOF', una palabra reservada u operador/puntuación literal
    lexema: str
    linea: int
    col: int

    def __repr__(self):
        return f"Token({self.tipo!r}, {self.lexema!r}, {self.linea}:{self.col})"


class LexError(Exception):
    pass


def tokenizar(texto: str):
    tokens, linea, inicio_linea = [], 1, 0
    for m in MASTER.finditer(texto):
        k, lex = m.lastgroup, m.group()
        col = m.start() - inicio_linea + 1
        if k == "NL":
            linea += 1
            inicio_linea = m.end()
        elif k in ("WS", "COMENT"):
            continue
        elif k == "ERROR":
            raise LexError(f"Carácter inesperado {lex!r} en {linea}:{col}")
        elif k == "ID":
            tokens.append(Token(lex if lex in KEYWORDS else "ID", lex, linea, col))
        elif k == "NUM":
            tokens.append(Token("NUM", lex, linea, col))
        else:  # OP1, OP2, PUNT: el tipo es el propio símbolo
            tokens.append(Token(lex, lex, linea, col))
    tokens.append(Token("EOF", "", linea, len(texto) - inicio_linea + 1))
    return tokens
