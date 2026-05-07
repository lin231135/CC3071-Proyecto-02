"""
Cálculo de los conjuntos PRIMERO para una Gramática Libre de Contexto.
Algoritmo 4.3 del Libro del Dragón (Aho et al.), §4.4.2.

PRIMERO(α) = conjunto de terminales que inician cadenas derivables desde α.
Si α puede derivar ε, entonces ε ∈ PRIMERO(α).
"""

from .grammar import Gramatica, EPSILON


def calcular_primero(gramatica: Gramatica) -> dict:
    """Retorna PRIMERO(X) para cada símbolo X de la gramática."""
    primero = {}

    # PRIMERO(a) = {a} para todo terminal
    for t in gramatica.terminales:
        primero[t] = {t}

    # PRIMERO(A) = {} para todo no terminal; se llena iterativamente
    for nt in gramatica.no_terminales:
        primero[nt] = set()

    # Iteración hasta punto fijo
    cambio = True
    while cambio:
        cambio = False
        for prod in gramatica.producciones:
            agregado = primero_de_cadena(prod.cuerpo, primero, gramatica)
            antes = len(primero[prod.cabeza])
            primero[prod.cabeza] |= agregado
            if len(primero[prod.cabeza]) > antes:
                cambio = True

    return primero


def primero_de_cadena(simbolos: list, primero: dict, gramatica: Gramatica) -> set:
    """
    Calcula PRIMERO de una cadena arbitraria  X1 X2 … Xn.
    Libro del Dragón §4.4.2:
      – Agregar PRIMERO(X1) − {ε}.
      – Si ε ∈ PRIMERO(X1), también agregar PRIMERO(X2) − {ε}, y así sucesivamente.
      – Si ε ∈ PRIMERO(Xi) para todo i, agregar ε.
    """
    resultado = set()

    # Cuerpo vacío -> producción epsilon
    if not simbolos:
        resultado.add(EPSILON)
        return resultado

    todos_nullable = True
    for simbolo in simbolos:
        # Los terminales aún no en el diccionario se tratan como {simbolo}
        prim_simbolo = primero.get(simbolo, {simbolo} if gramatica.es_terminal(simbolo) else set())
        resultado |= prim_simbolo - {EPSILON}

        if EPSILON not in prim_simbolo:
            todos_nullable = False
            break

    if todos_nullable:
        resultado.add(EPSILON)

    return resultado
