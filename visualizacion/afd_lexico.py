"""
Visualización del autómata finito determinista (AFD) del analizador léxico.
Usa Graphviz para generar un diagrama PNG y lo retorna como imagen PIL.
"""

import io
import graphviz
from PIL import Image


def generar_imagen_afd(estados_afd, estado_resaltado=None, color_resaltado="#add8e6"):
    """
    Genera una imagen PNG del AFD del lexer.

    Parámetros
    ----------
    estados_afd       list[EstadoAFD]
    estado_resaltado  str | None   — ID del estado a colorear
    color_resaltado   str          — color HTML para el estado resaltado
    """
    dot = graphviz.Digraph(
        graph_attr={"rankdir": "LR", "bgcolor": "#1e1e1e"},
        node_attr={"fontname": "Courier New", "fontsize": "9", "fontcolor": "white"},
        edge_attr={"fontname": "Arial", "fontsize": "8", "fontcolor": "#aaaaaa",
                   "color": "#666666"},
    )

    for est in estados_afd:
        shape     = "doublecircle" if est.es_aceptacion else "circle"
        fillcolor = color_resaltado if (estado_resaltado and est.id_estado == estado_resaltado) else "#2d2d2d"
        fontcolor = "#000000" if (estado_resaltado and est.id_estado == estado_resaltado) else "white"
        dot.node(est.id_estado, est.id_estado, shape=shape, style="filled",
                 fillcolor=fillcolor, fontcolor=fontcolor, color="#555555")

    dot.node("inicio", "", shape="none", width="0")
    if estados_afd:
        dot.edge("inicio", estados_afd[0].id_estado, color="white")

    for est in estados_afd:
        for char, dest in est.transiciones.items():
            dot.edge(est.id_estado, dest, label=char)

    return Image.open(io.BytesIO(dot.pipe(format="png")))
