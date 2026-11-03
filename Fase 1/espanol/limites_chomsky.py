"""
Lenguajes de la jerarquía de Chomsky y su relación con el español.

 Tipo 3 (regular)           a*b*                      -> autómata finito
 Tipo 2 (libre de contexto) a^n b^n                   -> autómata de pila
 Tipo 1 (sensible al ctx.)  a^n b^n c^n ,  w w        -> autómata linealmente acotado

Las dependencias cruzadas ("respectivamente") tienen la forma de w w:
    Ana, Luis, Marta  son  médica, ingeniero, abogada
    x1   x2    x3          y1       y2         y3     (xi se relaciona con yi)
Un CFG puede emparejar de forma ANIDADA (a^n b^n: el último abre, el primero
cierra, como una pila), pero no de forma CRUZADA (primero con primero), porque
una pila saca en orden inverso.

Prueba esquemática con el lema de bombeo para CFG (L = {a^n b^m c^n d^m}):
  Sea p la longitud de bombeo y z = a^p b^p c^p d^p = uvwxy con |vwx| <= p, |vx| >= 1.
  Como |vwx| <= p, vwx no puede tocar a la vez las 'a' y las 'c' (hay p b's en medio),
  ni las 'b' y las 'd'. Al bombear (i=2 ó i=0) se rompe la igualdad entre
  #a y #c, o entre #b y #d  =>  uv^i w x^i y  no pertenece a L. Contradicción. L no es CFL.
"""


def en_an_bn(s: str) -> bool:
    """Tipo 2: a^n b^n (n>=0). Lo reconoce una CFG: S -> a S b | ε."""
    n = len(s) // 2
    return s == "a" * n + "b" * n


def en_an_bn_cn(s: str) -> bool:
    """Tipo 1: a^n b^n c^n. NO existe CFG que lo genere."""
    n = len(s) // 3
    return s == "a" * n + "b" * n + "c" * n


def en_ww(s: str) -> bool:
    """Tipo 1: {ww}. Modelo de dependencias cruzadas de tipo 'respectivamente'."""
    h = len(s) // 2
    return len(s) % 2 == 0 and s[:h] == s[h:]


def respectivamente_ok(sujetos, atributos) -> bool:
    """
    Versión 'palpable' en español: se cumple si cada atributo concuerda en
    género con el sujeto de la MISMA posición. Requiere emparejar i-ésimo con
    i-ésimo (cruzado), algo que una CFG no hace para n arbitrario.
    sujetos y atributos: listas de géneros 'm'/'f'.
    """
    return len(sujetos) == len(atributos) and all(a == b for a, b in zip(sujetos, atributos))


if __name__ == "__main__":
    for nombre, f, casos in [
        ("a^n b^n   (tipo 2)", en_an_bn, ["", "ab", "aabb", "aab"]),
        ("a^n b^n c^n (tipo 1)", en_an_bn_cn, ["abc", "aabbcc", "aabbc"]),
        ("ww        (tipo 1)", en_ww, ["abab", "abba", "aa"]),
    ]:
        print(nombre, {c: f(c) for c in casos})
    # "Ana, Luis y Marta son médica, ingeniero y abogada, respectivamente"
    print("respectivamente:", respectivamente_ok(["f", "m", "f"], ["f", "m", "f"]),
          "| con desajuste:", respectivamente_ok(["f", "m", "f"], ["f", "f", "m"]))
