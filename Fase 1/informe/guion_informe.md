# Guion del informe (5-7 páginas)

## 1. Marco teórico (1 pág.)
Jerarquía de Chomsky (tipos 3→0), autómata asociado a cada nivel, lema de bombeo para CFL.
Diferencias formal vs natural: ambigüedad, recursividad, dependencias, concordancia.

## 2. Parser formal (1 pág.)
Gramática EBNF (ver docstring de `formal/parser.py`), eliminación de recursión izquierda
(`expr -> and_e ('||' and_e)*`), else colgante (única ambigüedad; se resuelve por convención),
recuperación de errores en modo pánico, resultados de `tests/test_formal.py`.

## 3. Extensión al español (1.5 pág.)
V1 → V2 → V3. Resultados medidos con `python -m espanol.experimento`:

| Gramática | Producciones | No terminales |
|---|---|---|
| V1 ingenua | 58 | 8 |
| V2 con concordancia | ~80 | 28 |
| V3 + relativa/PP/adverbio | ~104 | 33 |

Errores contra el juicio nativo (20 oraciones): V1 sobregenera en 3; V2 en 0 pero subgenera;
V3 deja 4 gramaticales sin cubrir (VS, sujeto nulo, coordinación, 'a' personal).

## 4. Análisis formal de fallas (1.5 pág.)  ← aquí está la nota de "profundidad"
Para cada fila: regla que falla → fenómeno → nivel de Chomsky.

| Fenómeno | ¿Excede CFG? | Explicación |
|---|---|---|
| Concordancia Det-N-Adj-V | **No** | Rasgos finitos ⇒ duplicar no terminales (V2). Costo: explosión de reglas y pérdida de generalización |
| Concordancia a distancia (relativa) | **No** | Se propaga con `Rel_n` (V3) |
| Ambigüedad PP-attachment | No es de poder generativo | La CFG la representa con 2 árboles; LL(1) no puede (exige 1 derivación) |
| SN -> SN Rel / SN SP | No | Recursión izquierda ⇒ imposible en LL(1)/descenso recursivo sin transformar; por eso se usa ChartParser |
| Orden VS, sujeto nulo, coordinación | No | Faltan reglas; es cuestión de cobertura, no de poder |
| Dependencias cruzadas ("respectivamente") | **Sí** | Forma {a^n b^m c^n d^m} / {ww}: no CFL (lema de bombeo, ver `limites_chomsky.py`) → tipo 1 (suave) |
| Ambigüedad léxica (la, como) | Fuera de la sintaxis pura | Requiere contexto/semántica |

Mensaje central: la mayoría de las "fallas" prácticas son de **escala y ambigüedad**, y solo
las dependencias cruzadas (y fenómenos similares) rebasan la CFG en sentido estricto.

## 5. Comparación con spaCy/NLTK (1 pág.)
Hallazgo medido con `demo_spacy`: spaCy analiza SIEMPRE, incluso "los niño duermen" (no valida
gramaticalidad, solo predice la estructura más probable); la CFG V3 rechaza y es exacta pero frágil.
spaCy no verifica que "respectivamente" empareje i-ésimo con i-ésimo.

## 6. Conclusiones
