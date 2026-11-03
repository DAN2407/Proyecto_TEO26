import unittest
from formal.parser import parsear
from formal.lexer import tokenizar, LexError

VALIDAS = [
    "int x;",
    "int x = 5;",
    "x = x + 1;",
    "x = (a + b) * c - d / 2 % 3;",
    "x = -a + !b;",
    "if (x < 3) y = 1;",
    "if (x < 3) y = 1; else y = 2;",
    "if (a) if (b) x = 1; else x = 2;",          # else colgante
    "while (i <= 10 && j != 0) { i = i + 1; }",
    "{ int a = 1; { int b = a; } }",
    "// comentario\nint z = 1 || 0 && 2 == 2;",
    "",                                          # programa vacío
]

INVALIDAS = [
    "int x",                 # falta ;
    "int = 5;",              # falta identificador
    "x = ;",                 # falta expresión
    "x = 3 +;",
    "if x < 3) y = 1;",      # falta (
    "while (x < 3 { }",      # falta )
    "{ int a = 1;",          # falta }
    "x = (1 + 2;",
    "else x = 1;",           # else sin if
    "3 = x;",                # lvalue inválido
]


class TestFormal(unittest.TestCase):
    def test_validas(self):
        for src in VALIDAS:
            with self.subTest(src=src):
                _, errs = parsear(src)
                self.assertEqual(errs, [], f"Debió aceptar: {src!r}")

    def test_invalidas(self):
        for src in INVALIDAS:
            with self.subTest(src=src):
                _, errs = parsear(src)
                self.assertTrue(errs, f"Debió rechazar: {src!r}")

    def test_lexer_error(self):
        with self.assertRaises(LexError):
            tokenizar("int x = 3 @ 4;")

    def test_precedencia(self):
        a, _ = parsear("x = 1 + 2 * 3;")
        self.assertIn("(Suma 1 + (Termino 2 * 3))", a.sexp())

    def test_else_colgante(self):
        a, _ = parsear("if (a) if (b) x = 1; else x = 2;")
        externo = a.hijos[0]
        self.assertEqual(len(externo.hijos), 5)    # if externo SIN else
        interno = externo.hijos[4]
        self.assertEqual(len(interno.hijos), 7)    # if interno CON else

    def test_recuperacion_multiples_errores(self):
        _, errs = parsear("int x\nint y = ;\nint z = 3;")
        self.assertGreaterEqual(len(errs), 2)

    def test_posicion_error(self):
        _, errs = parsear("int x = 1;\nint y = ;")
        self.assertIn("2:9", errs[0])


if __name__ == "__main__":
    unittest.main()
