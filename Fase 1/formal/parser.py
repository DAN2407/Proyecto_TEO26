"""
Parser descendente recursivo para un subconjunto de C.

GRAMÁTICA (EBNF, sin recursión por la izquierda; cada alternativa se decide
con 1 token de lookahead, es decir, LL(1)):

  programa   -> sentencia* EOF
  sentencia  -> decl | asign | if_st | while_st | bloque
  decl       -> 'int' ID ( '=' expr )? ';'
  asign      -> ID '=' expr ';'
  if_st      -> 'if' '(' expr ')' sentencia ( 'else' sentencia )?
  while_st   -> 'while' '(' expr ')' sentencia
  bloque     -> '{' sentencia* '}'

  expr       -> or_e
  or_e       -> and_e ( '||' and_e )*
  and_e      -> eq_e  ( '&&' eq_e )*
  eq_e       -> rel_e ( ('=='|'!=') rel_e )*
  rel_e      -> add_e ( ('<'|'>'|'<='|'>=') add_e )*
  add_e      -> term  ( ('+'|'-') term )*
  term       -> unario ( ('*'|'/'|'%') unario )*
  unario     -> ('-'|'!') unario | primario
  primario   -> NUM | ID | '(' expr ')'

Nota: el "else colgante" hace la gramática ligeramente ambigua; el parser lo
resuelve asociando 'else' con el 'if' más cercano (el 'if' consume el else
con '?' de forma voraz). Es la convención estándar de C.
"""
from .lexer import tokenizar, Token
from .tree import Node


class ParseError(Exception):
    def __init__(self, msg, tok: Token):
        super().__init__(f"Error sintáctico en {tok.linea}:{tok.col}: {msg}")
        self.tok = tok


class Parser:
    FIRST_SENT = {"int", "ID", "if", "while", "{"}

    def __init__(self, texto: str):
        self.toks = tokenizar(texto)
        self.i = 0
        self.errores = []

    # --- utilidades ---
    @property
    def act(self) -> Token:
        return self.toks[self.i]

    def consumir(self, tipo: str) -> Node:
        if self.act.tipo != tipo:
            esperado = {"ID": "un identificador", "NUM": "un número"}.get(tipo, f"'{tipo}'")
            encontrado = self.act.lexema or "fin de entrada"
            raise ParseError(f"se esperaba {esperado} y se encontró {encontrado!r}", self.act)
        t = self.act
        self.i += 1
        return Node(t.tipo, valor=t.lexema)

    def sincronizar(self):
        """Modo pánico: avanza hasta después de ';' o hasta '}' / inicio de sentencia."""
        while self.act.tipo != "EOF":
            if self.act.tipo == ";":
                self.i += 1
                return
            if self.act.tipo in ("}",) or self.act.tipo in self.FIRST_SENT:
                return
            self.i += 1

    # --- gramática ---
    def programa(self) -> Node:
        n = Node("Programa")
        while self.act.tipo != "EOF":
            antes = self.i
            try:
                n.hijos.append(self.sentencia())
            except ParseError as e:
                self.errores.append(str(e))
                self.sincronizar()
                if self.i == antes:      # garantizar progreso
                    self.i += 1
        return n

    def sentencia(self) -> Node:
        t = self.act.tipo
        if t == "int":   return self.decl()
        if t == "ID":    return self.asign()
        if t == "if":    return self.if_st()
        if t == "while": return self.while_st()
        if t == "{":     return self.bloque()
        raise ParseError(f"sentencia inválida, no puede empezar con {self.act.lexema or 'fin de entrada'!r}", self.act)

    def decl(self) -> Node:
        n = Node("Decl", [self.consumir("int"), self.consumir("ID")])
        if self.act.tipo == "=":
            n.hijos += [self.consumir("="), self.expr()]
        n.hijos.append(self.consumir(";"))
        return n

    def asign(self) -> Node:
        return Node("Asign", [self.consumir("ID"), self.consumir("="), self.expr(), self.consumir(";")])

    def if_st(self) -> Node:
        n = Node("If", [self.consumir("if"), self.consumir("("), self.expr(),
                        self.consumir(")"), self.sentencia()])
        if self.act.tipo == "else":
            n.hijos += [self.consumir("else"), self.sentencia()]
        return n

    def while_st(self) -> Node:
        return Node("While", [self.consumir("while"), self.consumir("("), self.expr(),
                              self.consumir(")"), self.sentencia()])

    def bloque(self) -> Node:
        n = Node("Bloque", [self.consumir("{")])
        while self.act.tipo not in ("}", "EOF"):
            n.hijos.append(self.sentencia())
        n.hijos.append(self.consumir("}"))
        return n

    # --- expresiones: un método por nivel de precedencia ---
    def expr(self) -> Node:
        return self._binario("Expr", self.and_e, ("||",))

    def and_e(self):  return self._binario("And", self.eq_e, ("&&",))
    def eq_e(self):   return self._binario("Igualdad", self.rel_e, ("==", "!="))
    def rel_e(self):  return self._binario("Relacional", self.add_e, ("<", ">", "<=", ">="))
    def add_e(self):  return self._binario("Suma", self.term, ("+", "-"))
    def term(self):   return self._binario("Termino", self.unario, ("*", "/", "%"))

    def _binario(self, nombre, sub, ops) -> Node:
        izq = sub()
        if self.act.tipo not in ops:
            return izq                 # colapsa niveles sin operador
        n = Node(nombre, [izq])
        while self.act.tipo in ops:
            n.hijos += [self.consumir(self.act.tipo), sub()]
        return n

    def unario(self) -> Node:
        if self.act.tipo in ("-", "!"):
            return Node("Unario", [self.consumir(self.act.tipo), self.unario()])
        return self.primario()

    def primario(self) -> Node:
        t = self.act.tipo
        if t in ("NUM", "ID"):
            return self.consumir(t)
        if t == "(":
            return Node("Grupo", [self.consumir("("), self.expr(), self.consumir(")")])
        raise ParseError(f"se esperaba una expresión y se encontró {self.act.lexema or 'fin de entrada'!r}", self.act)


def parsear(texto: str):
    """Devuelve (arbol, lista_de_errores). Lanza LexError si hay símbolos ilegales."""
    p = Parser(texto)
    arbol = p.programa()
    return arbol, p.errores
