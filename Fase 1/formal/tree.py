"""Nodos del árbol de análisis sintáctico."""
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Node:
    tipo: str                       # nombre del no terminal o del token hoja
    hijos: List["Node"] = field(default_factory=list)
    valor: Optional[str] = None     # lexema (solo en hojas)

    def pretty(self, prefijo: str = "", ultimo: bool = True, raiz: bool = True) -> str:
        etiqueta = self.tipo if (self.valor is None or self.valor == self.tipo) else f"{self.tipo}({self.valor})"
        if raiz:
            s = etiqueta + "\n"
            nuevo = ""
        else:
            s = prefijo + ("└── " if ultimo else "├── ") + etiqueta + "\n"
            nuevo = prefijo + ("    " if ultimo else "│   ")
        for i, h in enumerate(self.hijos):
            s += h.pretty(nuevo, i == len(self.hijos) - 1, False)
        return s

    def sexp(self) -> str:
        """Representación compacta, útil para pruebas."""
        if not self.hijos:
            return self.valor if self.valor is not None else self.tipo
        return f"({self.tipo} " + " ".join(h.sexp() for h in self.hijos) + ")"
