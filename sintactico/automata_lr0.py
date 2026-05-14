"""
Construcción del autómata LR(0) — colección canónica de ítems.
Libro del Dragón §4.6.2, Algoritmos 4.38–4.40.
"""

from gramatica.grammar import Gramatica, Produccion

SIMBOLO_PRIMA = "S'"


class ItemLR0:
    """Ítem LR(0): [A → α • β]  (el punto está en posición self.punto)."""

    __slots__ = ("produccion", "punto")

    def __init__(self, produccion: Produccion, punto: int = 0):
        self.produccion = produccion
        self.punto      = punto

    def simbolo_tras_punto(self):
        c = self.produccion.cuerpo
        return c[self.punto] if self.punto < len(c) else None

    def es_final(self) -> bool:
        return self.punto >= len(self.produccion.cuerpo)

    def avanzar(self) -> "ItemLR0":
        return ItemLR0(self.produccion, self.punto + 1)

    def __eq__(self, other):
        return (isinstance(other, ItemLR0)
                and self.produccion == other.produccion
                and self.punto == other.punto)

    def __hash__(self):
        return hash((self.produccion, self.punto))

    def __repr__(self):
        c = list(self.produccion.cuerpo)
        c.insert(self.punto, "•")
        return f"[{self.produccion.cabeza} → {' '.join(c) if c else '•'}]"


class EstadoLR0:
    """Estado del autómata LR(0)."""

    def __init__(self, id_estado: int, items: frozenset):
        self.id          = id_estado
        self.items       = items
        self.transiciones: dict = {}


# ── Algoritmos canónicos ───────────────────────────────────────────────────

def clausura(items: frozenset, gramatica: Gramatica) -> frozenset:
    """Clausura de un conjunto de ítems LR(0) — Algoritmo 4.38."""
    conjunto = set(items)
    cambiado = True
    while cambiado:
        cambiado = False
        nuevos = set()
        for item in conjunto:
            B = item.simbolo_tras_punto()
            if B is not None and gramatica.es_no_terminal(B):
                for prod in gramatica.producciones_de(B):
                    nuevo = ItemLR0(prod, 0)
                    if nuevo not in conjunto:
                        nuevos.add(nuevo)
                        cambiado = True
        conjunto |= nuevos
    return frozenset(conjunto)


def goto_lr0(items: frozenset, simbolo: str, gramatica: Gramatica) -> frozenset:
    """Función GOTO — Algoritmo 4.39."""
    movidos = frozenset(
        item.avanzar()
        for item in items
        if item.simbolo_tras_punto() == simbolo
    )
    return clausura(movidos, gramatica) if movidos else frozenset()


def construir_automata_lr0(gramatica: Gramatica):
    """
    Construye la colección canónica de conjuntos de ítems LR(0) — Algoritmo 4.40.

    Retorna:
        estados (list[EstadoLR0]), prod_aumentada (Produccion)
    """
    simbolo_aug = SIMBOLO_PRIMA
    while simbolo_aug in gramatica.no_terminales:
        simbolo_aug += "'"

    prod_aumentada  = Produccion(simbolo_aug, [gramatica.simbolo_inicio])
    item_inicial    = ItemLR0(prod_aumentada, 0)
    estado0_items   = clausura(frozenset([item_inicial]), gramatica)

    estados: list = []
    mapa:    dict = {}
    cola:    list = []

    def obtener_o_crear(items: frozenset) -> int:
        if items in mapa:
            return mapa[items]
        idx = len(estados)
        mapa[items] = idx
        estados.append(EstadoLR0(idx, items))
        cola.append(idx)
        return idx

    obtener_o_crear(estado0_items)

    simbolos = gramatica.terminales | gramatica.no_terminales

    while cola:
        id_actual = cola.pop(0)
        estado    = estados[id_actual]
        for sym in simbolos:
            destino_items = goto_lr0(estado.items, sym, gramatica)
            if destino_items:
                id_dest = obtener_o_crear(destino_items)
                estado.transiciones[sym] = id_dest

    return estados, prod_aumentada
