import sys
from .parser import parsear

if __name__ == "__main__":
    texto = open(sys.argv[1]).read() if len(sys.argv) > 1 else sys.stdin.read()
    arbol, errores = parsear(texto)
    if errores:
        print("\n".join(errores))
        sys.exit(1)
    print(arbol.pretty())
