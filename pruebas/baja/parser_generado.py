# =============================================================
# ANALIZADOR SINTÁCTICO SLR — GENERADO AUTOMÁTICAMENTE
# Este archivo es INDEPENDIENTE del generador.
# =============================================================

TABLA_ACTION = {
    0: {'ID': ('shift', 3)},
    1: {'$': ('reduce', 'programa', ('lista_stmt',)), 'ID': ('shift', 3)},
    2: {'$': ('accept', None)},
    3: {'ASSIGN': ('shift', 6)},
    4: {'ID': ('reduce', 'lista_stmt', ('stmt',)), '$': ('reduce', 'lista_stmt', ('stmt',))},
    5: {'ID': ('reduce', 'lista_stmt', ('lista_stmt', 'stmt')), '$': ('reduce', 'lista_stmt', ('lista_stmt', 'stmt'))},
    6: {'NUM': ('shift', 9), 'ID': ('shift', 10)},
    7: {'SEMI': ('shift', 11), 'PLUS': ('shift', 12)},
    8: {'SEMI': ('reduce', 'expr', ('term',)), 'PLUS': ('reduce', 'expr', ('term',))},
    9: {'SEMI': ('reduce', 'term', ('NUM',)), 'PLUS': ('reduce', 'term', ('NUM',))},
    10: {'SEMI': ('reduce', 'term', ('ID',)), 'PLUS': ('reduce', 'term', ('ID',))},
    11: {'ID': ('reduce', 'stmt', ('ID', 'ASSIGN', 'expr', 'SEMI')), '$': ('reduce', 'stmt', ('ID', 'ASSIGN', 'expr', 'SEMI'))},
    12: {'NUM': ('shift', 9), 'ID': ('shift', 10)},
    13: {'SEMI': ('reduce', 'expr', ('expr', 'PLUS', 'term')), 'PLUS': ('reduce', 'expr', ('expr', 'PLUS', 'term'))},
}

TABLA_GOTO = {
    0: {'lista_stmt': 1, 'stmt': 4, 'programa': 2},
    1: {'stmt': 5},
    2: {},
    3: {},
    4: {},
    5: {},
    6: {'expr': 7, 'term': 8},
    7: {},
    8: {},
    9: {},
    10: {},
    11: {},
    12: {'term': 13},
    13: {},
}

PRODUCCIONES = [
    ("S'", ('programa',)),
    ('programa', ('lista_stmt',)),
    ('lista_stmt', ('lista_stmt', 'stmt')),
    ('lista_stmt', ('stmt',)),
    ('stmt', ('ID', 'ASSIGN', 'expr', 'SEMI')),
    ('expr', ('expr', 'PLUS', 'term')),
    ('expr', ('term',)),
    ('term', ('ID',)),
    ('term', ('NUM',)),
]

TOKENS_IGNORADOS = {'WS'}


def _tipo_token(accion: str) -> str:
    """
    Extrae el nombre del tipo de token de la acción producida por el lexer.
    Ejemplos:  'return INT' -> 'INT',   'INT' -> 'INT'
    """
    accion = accion.strip()
    partes = accion.split()
    if not partes:
        return accion
    if partes[0].lower() == "return" and len(partes) > 1:
        return partes[1]
    return partes[-1]


def parsear(tokens_lexer: list):
    """
    Ejecuta el análisis sintáctico SLR.

    Parámetros
    ----------
    tokens_lexer : list[(lexema, accion)]  — salida de scanner_generado.escanear()

    Retorna
    -------
    (exito: bool, pasos: list[str], errores: list[str])
    """
    pasos = []
    errores = []

    # Filtrar tokens ignorados; acumular errores léxicos sin detener el análisis
    tokens = []
    for lexema, accion in tokens_lexer:
        if "ERROR" in accion.upper():
            errores.append(f"ERROR LÉXICO: símbolo no reconocido '{lexema}'")
            continue
        tipo = _tipo_token(accion)
        if tipo not in TOKENS_IGNORADOS:
            tokens.append((lexema, tipo))
    if errores:
        return False, pasos, errores

    # Agregar marca de fin
    tokens.append(("$", "$"))

    pila = [0]
    idx = 0

    col_p = 40
    col_e = 30
    pasos.append(f"{'Pila':<{col_p}} {'Entrada':<{col_e}} Acción")
    pasos.append("-" * (col_p + col_e + 20))

    while True:
        estado = pila[-1]
        lexema, tipo = tokens[idx]

        pila_str  = " ".join(str(s) for s in pila)
        entr_str  = " ".join(t for _, t in tokens[idx : idx + 6])
        if len(tokens) - idx > 6:
            entr_str += " …"

        if estado not in TABLA_ACTION or tipo not in TABLA_ACTION[estado]:
            esperados = sorted(TABLA_ACTION.get(estado, {}).keys())
            msg = (
                f"ERROR SINTÁCTICO: token inesperado '{lexema}' "
                f"(tipo {tipo}) en estado {estado}. "
                f"Se esperaba: {esperados}"
            )
            pasos.append(f"{pila_str:<{col_p}} {entr_str:<{col_e}} ERROR")
            errores.append(msg)
            return False, pasos, errores

        accion = TABLA_ACTION[estado][tipo]
        tipo_acc = accion[0]

        if tipo_acc == "shift":
            j = accion[1]
            pasos.append(f"{pila_str:<{col_p}} {entr_str:<{col_e}} Desplazar '{lexema}' → s{j}")
            pila.append(j)
            idx += 1

        elif tipo_acc == "reduce":
            cabeza, cuerpo = accion[1], accion[2]
            prod_str = f"{cabeza} → {' '.join(cuerpo) if cuerpo else 'ε'}"
            pasos.append(f"{pila_str:<{col_p}} {entr_str:<{col_e}} Reducir {prod_str}")

            if cuerpo:
                pila = pila[: -len(cuerpo)]

            top = pila[-1]
            if top not in TABLA_GOTO or cabeza not in TABLA_GOTO[top]:
                errores.append(
                    f"ERROR SINTÁCTICO: no hay GOTO[{top}, {cabeza}]"
                )
                return False, pasos, errores

            pila.append(TABLA_GOTO[top][cabeza])

        elif tipo_acc == "accept":
            pasos.append(f"{pila_str:<{col_p}} {entr_str:<{col_e}} ACEPTAR ✓")
            return True, pasos, errores

    return False, pasos, errores   # no alcanzable


if __name__ == "__main__":
    import sys
    import importlib.util

    if len(sys.argv) < 3:
        print("Uso: python parser_generado.py scanner_generado.py entrada.txt")
        sys.exit(1)

    spec = importlib.util.spec_from_file_location("scanner_generado", sys.argv[1])
    scanner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(scanner)

    with open(sys.argv[2], "r", encoding="utf-8") as f:
        texto = f.read()

    tok_lex = scanner.escanear(texto)
    exito, pasos, errores = parsear(tok_lex)

    for p in pasos:
        print(p)
    if errores:
        print()
        for e in errores:
            print(e)
    sys.exit(0 if exito else 1)
