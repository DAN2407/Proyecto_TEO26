"""
Intentos de extender una CFG al español (Fase 1).

Se construyen TRES gramáticas con NLTK:

  V1  "ingenua": sin concordancia. Sobregenera (acepta "los niño duermen").
  V2  "con rasgos expandidos": la concordancia de género/número se codifica
      DUPLICANDO no terminales (SN_ms, SN_fp, SV_3s, ...). Sigue siendo CFG,
      pero el número de reglas explota y desaparece la generalización.
  V3  V2 + cláusula relativa ("que") + frases preposicionales + adverbios.
      Aquí aparece la ambigüedad estructural (PP-attachment).

Uso:  python -m espanol.gramatica_es
"""
import itertools
import nltk

# ----------------------------------------------------------------- léxico
# (forma, género, número). 'x' = invariable en género.
DET = [("el", "m", "s"), ("la", "f", "s"), ("los", "m", "p"), ("las", "f", "p"),
       ("un", "m", "s"), ("una", "f", "s"), ("unos", "m", "p"), ("unas", "f", "p")]
NOM = [("niño", "m", "s"), ("niña", "f", "s"), ("niños", "m", "p"), ("niñas", "f", "p"),
       ("perro", "m", "s"), ("perra", "f", "s"), ("perros", "m", "p"), ("perras", "f", "p"),
       ("libro", "m", "s"), ("libros", "m", "p"), ("casa", "f", "s"), ("casas", "f", "p"),
       ("telescopio", "m", "s"), ("hombre", "m", "s"), ("mujer", "f", "s")]
ADJ = [("pequeño", "m", "s"), ("pequeña", "f", "s"), ("pequeños", "m", "p"), ("pequeñas", "f", "p"),
       ("rojo", "m", "s"), ("roja", "f", "s"), ("rojos", "m", "p"), ("rojas", "f", "p"),
       ("feliz", "m", "s"), ("feliz", "f", "s"), ("felices", "m", "p"), ("felices", "f", "p")]
# verbos: (forma, número) 3ª persona, presente
VI = [("duerme", "s"), ("duermen", "p"), ("corre", "s"), ("corren", "p"), ("come", "s"), ("comen", "p")]
VT = [("lee", "s"), ("leen", "p"), ("ve", "s"), ("ven", "p"), ("come", "s"), ("comen", "p")]
VT_PRET = [("leyó", "s"), ("leyeron", "p"), ("vio", "s"), ("vieron", "p")]
ADV = ["rápidamente", "ayer", "mucho"]
PREP = ["con", "en", "de"]
PROPIOS = [("Ana", "f", "s"), ("Luis", "m", "s")]


def _q(w):  # comillas para NLTK
    return f"'{w}'"


# ----------------------------------------------------------------- V1
def gramatica_v1() -> str:
    reglas = [
        "S -> SN SV",
        "SN -> Det N | Det N Adj | Det Adj N | PN",
        "SV -> V | V SN",
        "Det -> " + " | ".join(_q(d[0]) for d in dict.fromkeys(DET)),
        "N -> " + " | ".join(_q(n[0]) for n in NOM),
        "Adj -> " + " | ".join(_q(a[0]) for a in dict.fromkeys(ADJ)),
        "PN -> " + " | ".join(_q(p[0]) for p in PROPIOS),
        "V -> " + " | ".join(_q(v[0]) for v in VI + VT + VT_PRET),
    ]
    return "\n".join(reglas)


# ----------------------------------------------------------------- V2 / V3
GEN, NUM = ("m", "f"), ("s", "p")


def gramatica_v2(extendida: bool = False) -> str:
    """Concordancia por duplicación de no terminales. extendida=True => V3."""
    r = []
    r.append("S -> " + " | ".join(f"SN_{g}{n} SV_{n}" for g in GEN for n in NUM) + " | SN_pn SV_s")
    for g, n in itertools.product(GEN, NUM):
        alt = [f"Det_{g}{n} N_{g}{n}",
               f"Det_{g}{n} N_{g}{n} Adj_{g}{n}",
               f"Det_{g}{n} Adj_{g}{n} N_{g}{n}"]
        if extendida:
            alt += [f"SN_{g}{n} Rel_{n}", f"SN_{g}{n} SP"]
        r.append(f"SN_{g}{n} -> " + " | ".join(alt))
    r.append("SN_pn -> PN" + (" | SN_pn SP" if extendida else ""))
    for n in NUM:
        sv = [f"V_i_{n}", f"V_t_{n} SNobj", f"V_tp_{n} SNobj"]
        if extendida:
            sv += [f"V_i_{n} Adv", f"V_t_{n} SNobj Adv", f"SV_{n} SP"]
        r.append(f"SV_{n} -> " + " | ".join(sv))
    r.append("SNobj -> " + " | ".join(f"SN_{g}{n}" for g in GEN for n in NUM) + " | SN_pn")
    if extendida:
        for n in NUM:
            r.append(f"Rel_{n} -> 'que' SV_{n}")      # el verbo concuerda con el antecedente
        r.append("SP -> Prep SNobj")
        r.append("Prep -> " + " | ".join(_q(p) for p in PREP))
        r.append("Adv -> " + " | ".join(_q(a) for a in ADV))
    # léxico
    for g, n in itertools.product(GEN, NUM):
        r.append(f"Det_{g}{n} -> " + " | ".join(_q(w) for w, gg, nn in DET if (gg, nn) == (g, n)))
        r.append(f"N_{g}{n} -> " + " | ".join(_q(w) for w, gg, nn in NOM if (gg, nn) == (g, n)))
        r.append(f"Adj_{g}{n} -> " + " | ".join(_q(w) for w, gg, nn in ADJ if (gg, nn) == (g, n)))
    r.append("PN -> " + " | ".join(_q(p[0]) for p in PROPIOS))
    for n in NUM:
        r.append(f"V_i_{n} -> " + " | ".join(_q(w) for w, nn in VI if nn == n))
        r.append(f"V_t_{n} -> " + " | ".join(_q(w) for w, nn in VT if nn == n))
        r.append(f"V_tp_{n} -> " + " | ".join(_q(w) for w, nn in VT_PRET if nn == n))
    return "\n".join(r)


def cargar(txt: str) -> nltk.CFG:
    return nltk.CFG.fromstring(txt)


def parsear(gram: nltk.CFG, oracion: str, max_arboles: int = 50):
    """Devuelve lista de árboles ([] si la oración no pertenece al lenguaje)."""
    toks = oracion.replace(",", " ").split()
    try:
        # los terminales deben estar en el léxico; si no, NLTK lanza ValueError
        return list(itertools.islice(nltk.ChartParser(gram).parse(toks), max_arboles))
    except ValueError:
        return []


def n_reglas(gram: nltk.CFG) -> int:
    return len(gram.productions())


if __name__ == "__main__":
    for nombre, g in [("V1 ingenua", cargar(gramatica_v1())),
                      ("V2 rasgos expandidos", cargar(gramatica_v2())),
                      ("V3 + rel/PP/adv", cargar(gramatica_v2(True)))]:
        print(f"{nombre:<24} producciones: {n_reglas(g):>4}   no terminales: {len({p.lhs() for p in g.productions()})}")
