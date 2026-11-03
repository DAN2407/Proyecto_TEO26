"""
Oraciones de prueba. Cada entrada: (oración, ¿gramatical en español?, fenómeno).
'gramatical' es el juicio de un hablante nativo, NO lo que haga la gramática.
"""
ORACIONES = [
    # --- núcleo: debe aceptarse ---
    ("el niño duerme",                                   True,  "básica"),
    ("las niñas leen un libro",                          True,  "básica"),
    ("Ana ve a la mujer",                                True,  "'a' personal (preposición exigida por el objeto)"),
    ("el perro pequeño come",                            True,  "adjetivo posnominal"),
    ("la casa roja duerme",                              True,  "adjetivo (semántica rara, sintaxis ok)"),
    ("Luis leyó el libro",                               True,  "pretérito"),
    # --- concordancia: debe rechazarse ---
    ("los niño duermen",                                 False, "concordancia Det-N número"),
    ("el niña duerme",                                   False, "concordancia Det-N género"),
    ("los niños duerme",                                 False, "concordancia sujeto-verbo"),
    ("la casa roja pequeños duerme",                     False, "concordancia adjetivo"),
    # --- subordinadas y modificadores ---
    ("el niño que lee el libro duerme",                  True,  "relativa"),
    ("los niños que leen un libro duermen",              True,  "relativa + concordancia a distancia"),
    ("los niños que lee un libro duermen",               False, "concordancia en relativa"),
    ("el niño corre rápidamente",                        True,  "adverbio"),
    ("el niño lee el libro en la casa",                  True,  "frase preposicional (también ambigua: 2 árboles)"),
    # --- ambigüedad estructural ---
    ("el hombre ve la mujer con el telescopio",          True,  "ambigüedad PP-attachment (2 lecturas)"),
    # --- fenómenos que exceden la CFG o la gramática ---
    ("duermen los niños",                                True,  "orden VS / inversión"),
    ("leen un libro",                                    True,  "sujeto nulo (pro-drop)"),
    ("Ana duerme y Luis corre",                          True,  "coordinación de oraciones"),
    ("el niño feliz duerme",                             True,  "adjetivo invariable en género"),
]

# Fenómeno de dependencias cruzadas: NO se puede evaluar con la CFG; se
# demuestra aparte en espanol/limites_chomsky.py
RESPECTIVAMENTE = "Ana, Luis y Marta son médica, ingeniero y abogada, respectivamente"
