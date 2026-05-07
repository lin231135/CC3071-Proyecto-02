"""
Cálculo de los conjuntos SIGUIENTE para una Gramática Libre de Contexto.
Algoritmo 4.3 del Libro del Dragón (Aho et al.), §4.4.2.

SIGUIENTE(A) = conjunto de terminales (y $) que pueden aparecer
inmediatamente a la derecha de A en alguna forma sentencial.
"""

from .grammar import Gramatica, EPSILON, MARCA_FIN
from .first_sets import primero_de_cadena


def calcular_siguiente(gramatica: Gramatica, primero: dict) -> dict:
    """
    Retorna SIGUIENTE(A) para cada no terminal A.
    Requiere los conjuntos PRIMERO ya calculados.

    Reglas del Libro del Dragón §4.4.2:
      1. $ ∈ SIGUIENTE(S)  donde S es el símbolo inicial.
      2. A → αBβ  ⇒  PRIMERO(β) − {ε} ⊆ SIGUIENTE(B).
      3. A → αB, o A → αBβ con ε ∈ PRIMERO(β)  ⇒  SIGUIENTE(A) ⊆ SIGUIENTE(B).
    """
    siguiente = {nt: set() for nt in gramatica.no_terminales}

    # Regla 1: $ pertenece al SIGUIENTE del símbolo inicial
    if gramatica.simbolo_inicio:
        siguiente[gramatica.simbolo_inicio].add(MARCA_FIN)

    # Iteración hasta punto fijo
    cambio = True
    while cambio:
        cambio = False
        for prod in gramatica.producciones:
            cabeza = prod.cabeza
            cuerpo = prod.cuerpo

            for i, simbolo in enumerate(cuerpo):
                if not gramatica.es_no_terminal(simbolo):
                    continue

                # β = resto del cuerpo después de la posición i
                beta = cuerpo[i + 1:]
                primero_beta = primero_de_cadena(beta, primero, gramatica)

                # Regla 2: PRIMERO(β) − {ε} ⊆ SIGUIENTE(simbolo)
                antes = len(siguiente[simbolo])
                siguiente[simbolo] |= primero_beta - {EPSILON}
                if len(siguiente[simbolo]) > antes:
                    cambio = True

                # Regla 3: si ε ∈ PRIMERO(β), entonces SIGUIENTE(cabeza) ⊆ SIGUIENTE(simbolo)
                if EPSILON in primero_beta:
                    antes = len(siguiente[simbolo])
                    siguiente[simbolo] |= siguiente[cabeza]
                    if len(siguiente[simbolo]) > antes:
                        cambio = True

    return siguiente