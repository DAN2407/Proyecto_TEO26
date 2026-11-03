"""
Demo: la misma lista de oraciones analizada por (a) la CFG V3 y (b) spaCy.

Requisitos:
    pip install spacy nltk
    python -m spacy download es_core_news_sm

Uso:
    python -m nlp_demo.demo_spacy            # todas las oraciones
    python -m nlp_demo.demo_spacy "los niño duermen"   # una oración
"""
import sys
import spacy
from espanol.gramatica_es import cargar, gramatica_v2, parsear
from espanol.oraciones import ORACIONES, RESPECTIVAMENTE

nlp = spacy.load("es_core_news_sm")
G3 = cargar(gramatica_v2(True))


def mostrar(s, nativo=None, fenomeno=""):
    print("=" * 90)
    print(f"ORACIÓN: {s}" + (f"   [nativo: {'gramatical' if nativo else 'agramatical'}; {fenomeno}]" if nativo is not None else ""))
    arboles = parsear(G3, s)
    print(f"  CFG V3 -> {'RECHAZA' if not arboles else f'{len(arboles)} árbol(es)'}")
    for a in arboles[:2]:
        print("   ", a.pformat(margin=200).replace("\n", ""))
    doc = nlp(s)
    print("  spaCy  -> (siempre produce un análisis)")
    for t in doc:
        m = t.morph.to_dict()
        print(f"     {t.text:<12}{t.pos_:<7}{t.dep_:<9}cabeza={t.head.text:<10}"
              f"Gen={m.get('Gender','-'):<5}Num={m.get('Number','-')}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        mostrar(" ".join(sys.argv[1:]))
    else:
        for s, ok, f in ORACIONES:
            mostrar(s, ok, f)
        mostrar(RESPECTIVAMENTE, True, "dependencias cruzadas")
