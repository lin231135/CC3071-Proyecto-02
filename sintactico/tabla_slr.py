"""
Construcción de las tablas SLR(1): ACTION y GOTO.
Libro del Dragón §4.6.2, Algoritmo 4.46.

  ACTION[i, a] = shift j  | reduce A→α  | accept  | error
  GOTO[i, A]   = j
"""

from gramatica.grammar     import Gramatica, MARCA_FIN
from gramatica.first_sets  import calcular_primero
from gramatica.follow_sets import calcular_siguiente
from sintactico.automata_lr0 import construir_automata_lr0

SHIFT  = "shift"
REDUCE = "reduce"
ACCEPT = "accept"


def construir_tabla_slr(gramatica: Gramatica):
    """
    Construye las tablas SLR.

    Retorna:
        estados            list[EstadoLR0]
        prod_aumentada     Produccion
        tabla_action       dict[int, dict[str, tuple]]
        tabla_goto         dict[int, dict[str, int]]
        conflictos         list[str]
        todas_prods        list[Produccion]   (aumentada en [0])
    """
    estados, prod_aumentada = construir_automata_lr0(gramatica)
    primero   = calcular_primero(gramatica)
    siguiente = calcular_siguiente(gramatica, primero)

    tabla_action: dict = {}
    tabla_goto:   dict = {}
    conflictos:   list = []

    todas_prods = [prod_aumentada] + list(gramatica.producciones)

    for estado in estados:
        ta: dict = {}
        tg: dict = {}

        for item in estado.items:
            sym = item.simbolo_tras_punto()

            if sym is not None:
                if gramatica.es_terminal(sym) and sym in estado.transiciones:
                    nueva = (SHIFT, estado.transiciones[sym])
                    if sym in ta and ta[sym] != nueva:
                        conflictos.append(
                            f"Conflicto S/S en estado {estado.id}, '{sym}'"
                        )
                    ta[sym] = nueva

                elif gramatica.es_no_terminal(sym) and sym in estado.transiciones:
                    tg[sym] = estado.transiciones[sym]

            else:
                if item.produccion == prod_aumentada:
                    ta[MARCA_FIN] = (ACCEPT, None)
                else:
                    cab = item.produccion.cabeza
                    for a in siguiente.get(cab, set()):
                        nueva = (REDUCE, item.produccion)
                        if a in ta and ta[a] != nueva:
                            conflictos.append(
                                f"Conflicto S/R o R/R en estado {estado.id}, '{a}'"
                            )
                        else:
                            ta[a] = nueva

        # GOTO desde transiciones a no terminales
        for sym, dest in estado.transiciones.items():
            if gramatica.es_no_terminal(sym):
                tg[sym] = dest

        tabla_action[estado.id] = ta
        tabla_goto[estado.id]   = tg

    return estados, prod_aumentada, tabla_action, tabla_goto, conflictos, todas_prods
