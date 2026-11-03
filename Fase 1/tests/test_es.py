"""Pruebas de las gramáticas del español: documentan lo que SÍ logra la CFG."""
import unittest
from espanol.gramatica_es import cargar, gramatica_v1, gramatica_v2, parsear, n_reglas
from espanol.limites_chomsky import en_an_bn, en_an_bn_cn, en_ww

V1, V2, V3 = cargar(gramatica_v1()), cargar(gramatica_v2()), cargar(gramatica_v2(True))


class TestEspanol(unittest.TestCase):
    def test_v1_sobregenera(self):
        self.assertTrue(parsear(V1, "los niño duermen"))        # no debería aceptarse

    def test_v2_concordancia_basica(self):
        self.assertTrue(parsear(V2, "los niños duermen"))
        for mala in ["los niño duermen", "el niña duerme", "los niños duerme"]:
            self.assertFalse(parsear(V2, mala), mala)

    def test_v3_relativa_concordancia_a_distancia(self):
        self.assertTrue(parsear(V3, "los niños que leen un libro duermen"))
        self.assertFalse(parsear(V3, "los niños que lee un libro duermen"))

    def test_ambiguedad_pp(self):
        self.assertEqual(len(parsear(V3, "el hombre ve la mujer con el telescopio")), 2)

    def test_limites_conocidos(self):
        # Orden VS, sujeto nulo y coordinación NO están cubiertos
        for s in ["duermen los niños", "leen un libro", "Ana duerme y Luis corre"]:
            self.assertFalse(parsear(V3, s), s)

    def test_explosion_de_reglas(self):
        self.assertGreater(n_reglas(V2), n_reglas(V1))
        self.assertGreater(n_reglas(V3), n_reglas(V2))

    def test_lenguajes_chomsky(self):
        self.assertTrue(en_an_bn("aabb")); self.assertFalse(en_an_bn("aab"))
        self.assertTrue(en_an_bn_cn("aabbcc")); self.assertFalse(en_an_bn_cn("aabbc"))
        self.assertTrue(en_ww("abab")); self.assertFalse(en_ww("abba"))


if __name__ == "__main__":
    unittest.main()
