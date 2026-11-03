"""
Demo con NLTK solamente (sin modelos descargables): muestra el árbol que
produce la CFG V3 y la ambigüedad PP-attachment con dos árboles.
"""
from espanol.gramatica_es import cargar, gramatica_v2, parsear

g = cargar(gramatica_v2(True))
for s in ["el hombre ve la mujer con el telescopio", "los niños que leen un libro duermen"]:
    arboles = parsear(g, s)
    print(f"\n{s!r}: {len(arboles)} árbol(es)")
    for a in arboles:
        a.pretty_print()
