# Proyecto TLP02-2026 – Fase 1
Gramáticas formales y lenguaje natural: los límites de la jerarquía de Chomsky.

## Instalación
```bash
pip install -r requirements.txt
python -m spacy download es_core_news_sm
```

## Cómo ejecutar
| Qué | Comando |
|---|---|
| Parser formal (subconjunto de C) sobre un archivo | `python -m formal programa.c` |
| Parser formal desde stdin | `echo "int x = 2;" \| python -m formal` |
| Todas las pruebas | `python -m unittest discover -s tests -t .` |
| Tamaño de las gramáticas del español (V1/V2/V3) | `python -m espanol.gramatica_es` |
| Tabla de aciertos/fallos de la CFG en español | `python -m espanol.experimento` |
| Lenguajes de la jerarquía de Chomsky | `python -m espanol.limites_chomsky` |
| Demo NLTK (árboles + ambigüedad) | `python -m nlp_demo.demo_nltk` |
| Demo spaCy vs CFG | `python -m nlp_demo.demo_spacy ["oración"]` |

## Estructura
- `formal/` lexer, parser descendente recursivo (LL(1)) y árbol. La gramática está documentada en el docstring de `parser.py`.
- `espanol/` gramáticas V1 (ingenua), V2 (concordancia por rasgos expandidos), V3 (+ relativas, PP, adverbios), oraciones etiquetadas y análisis de límites.
- `nlp_demo/` comparación con NLTK y spaCy.
- `tests/` pruebas del parser formal (válidas/inválidas/errores) y del español.
