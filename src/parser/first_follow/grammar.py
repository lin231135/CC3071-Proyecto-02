"""
Estructuras de datos para una Gramática Libre de Contexto (GLC).
Basado en el Libro del Dragón §4.1: G = (V, T, P, S).
"""

EPSILON = 'ε'
MARCA_FIN = '$'


class Produccion:
    """
    Regla de la forma  A → α
    Si el cuerpo es una lista vacía, representa una producción epsilon (A → ε).
    """

    def __init__(self, cabeza: str, cuerpo: list):
        self.cabeza = cabeza
        self.cuerpo = list(cuerpo)

    def es_epsilon(self) -> bool:
        return len(self.cuerpo) == 0

    def __repr__(self):
        cuerpo_str = ' '.join(self.cuerpo) if self.cuerpo else EPSILON
        return f"{self.cabeza} → {cuerpo_str}"

    def __eq__(self, other):
        return (isinstance(other, Produccion)
                and self.cabeza == other.cabeza
                and self.cuerpo == other.cuerpo)

    def __hash__(self):
        return hash((self.cabeza, tuple(self.cuerpo)))


class Gramatica:
    """
    Gramática Libre de Contexto  G = (V, T, P, S).
      V  – no terminales
      T  – terminales
      P  – lista ordenada de producciones
      S  – símbolo inicial
    """

    def __init__(self):
        self.terminales: set = set()
        self.no_terminales: set = set()
        self.producciones: list = []
        self.simbolo_inicio: str = None

    # Escritura

    def agregar_produccion(self, cabeza: str, cuerpo: list):
        prod = Produccion(cabeza, cuerpo)
        if prod not in self.producciones:
            self.producciones.append(prod)

    # Consultas 

    def producciones_de(self, simbolo: str) -> list:
        return [p for p in self.producciones if p.cabeza == simbolo]

    def es_terminal(self, simbolo: str) -> bool:
        return simbolo in self.terminales

    def es_no_terminal(self, simbolo: str) -> bool:
        return simbolo in self.no_terminales

    def __repr__(self):
        lineas = [
            f"Inicio        : {self.simbolo_inicio}",
            f"No terminales : {{{', '.join(sorted(self.no_terminales))}}}",
            f"Terminales    : {{{', '.join(sorted(self.terminales))}}}",
            "Producciones  :",
        ]
        for p in self.producciones:
            lineas.append(f"  {p}")
        return '\n'.join(lineas)
