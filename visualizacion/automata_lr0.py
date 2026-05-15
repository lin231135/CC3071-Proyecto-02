"""
Visualización del autómata LR(0).
Usa Graphviz para generar un diagrama PNG y lo retorna como imagen PIL.
"""

import io
from PIL import Image

try:
    import graphviz as gv
    _OK = True
except ImportError:
    _OK = False


def generar_imagen_lr0(estados, estado_resaltado=None, color_resaltado="#add8e6"):
    """
    Genera el diagrama del autómata LR(0) como imagen PIL.

    Parámetros
    ----------
    estados           list[EstadoLR0]
    estado_resaltado  int | None
    color_resaltado   str
    """
    if not _OK:
        raise RuntimeError("Instala 'graphviz': pip install graphviz")

    dot = gv.Digraph(
        comment="Autómata LR(0)",
        graph_attr={"rankdir": "LR", "bgcolor": "#1e1e1e", "fontname": "Courier New"},
        node_attr={"fontname": "Courier New", "fontsize": "8", "fontcolor": "white"},
        edge_attr={"fontname": "Arial",       "fontsize": "8", "fontcolor": "#aaaaaa",
                   "color": "#666666"},
    )

    dot.node("__init__", "", shape="none", width="0")
    dot.edge("__init__", "0", color="white")

    for estado in estados:
        items_str = "\\n".join(repr(it) for it in sorted(estado.items, key=repr))
        label = f"I{estado.id}\\n{'─'*20}\\n{items_str}"

        fill = color_resaltado if estado_resaltado == estado.id else "#2d2d2d"
        font = "#000000"       if estado_resaltado == estado.id else "white"

        dot.node(str(estado.id), label=label,
                 shape="rectangle", style="filled",
                 fillcolor=fill, fontcolor=font, color="#555555")

    for estado in estados:
        for simbolo, dest in estado.transiciones.items():
            dot.edge(str(estado.id), str(dest), label=simbolo)

    return Image.open(io.BytesIO(dot.pipe(format="png")))
