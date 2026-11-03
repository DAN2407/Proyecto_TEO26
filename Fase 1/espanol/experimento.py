"""Corre las oraciones contra V1, V2 y V3 y muestra una tabla comparativa."""
from .gramatica_es import cargar, gramatica_v1, gramatica_v2, parsear
from .oraciones import ORACIONES


def main():
    gs = {"V1": cargar(gramatica_v1()), "V2": cargar(gramatica_v2()), "V3": cargar(gramatica_v2(True))}
    print(f"{'oración':<46}{'nativo':<8}{'V1':>4}{'V2':>4}{'V3':>4}  fenómeno")
    print("-" * 110)
    err = {k: {"falso_pos": 0, "falso_neg": 0} for k in gs}
    for s, gram_ok, fen in ORACIONES:
        n = {k: len(parsear(g, s)) for k, g in gs.items()}
        for k in gs:
            if n[k] > 0 and not gram_ok: err[k]["falso_pos"] += 1
            if n[k] == 0 and gram_ok:    err[k]["falso_neg"] += 1
        print(f"{s:<46}{'sí' if gram_ok else 'no':<8}{n['V1']:>4}{n['V2']:>4}{n['V3']:>4}  {fen}")
    print("\n(Columnas V*: número de árboles de derivación; 0 = rechazada, >1 = ambigua)")
    print("\nErrores respecto al juicio del hablante nativo:")
    for k, e in err.items():
        print(f"  {k}: sobregeneración (acepta agramaticales) = {e['falso_pos']}, "
              f"subgeneración (rechaza gramaticales) = {e['falso_neg']}")


if __name__ == "__main__":
    main()
