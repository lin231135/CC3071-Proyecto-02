"""
Genera un archivo Python independiente que implementa el analizador sintáctico SLR.
El archivo generado NO importa ningún módulo del generador.
"""


def generar_parser_independiente(
    tabla_action: dict,
    tabla_goto: dict,
    todas_prods: list,
    tokens_ignorados: set,
    ruta_salida: str = "parser_generado.py",
) -> str:
    """
    Escribe el archivo parser_generado.py con las tablas SLR embebidas.

    Parámetros
    ----------
    tabla_action   dict[int, dict[str, tuple]]
    tabla_goto     dict[int, dict[str, int]]
    todas_prods    list[Produccion]  (producción aumentada en posición 0)
    tokens_ignorados  set[str]
    ruta_salida    ruta del archivo a generar
    """

    # ── Serializar ACTION ──────────────────────────────────────────────────
    action_lines = "{\n"
    for estado_id, acciones in sorted(tabla_action.items()):
        acc_dict: dict = {}
        for terminal, accion in acciones.items():
            tipo = accion[0]
            if tipo == "shift":
                acc_dict[terminal] = ("shift", accion[1])
            elif tipo == "reduce":
                prod = accion[1]
                acc_dict[terminal] = ("reduce", prod.cabeza, tuple(prod.cuerpo))
            elif tipo == "accept":
                acc_dict[terminal] = ("accept", None)
        action_lines += f"    {estado_id}: {repr(acc_dict)},\n"
    action_lines += "}"

    # ── Serializar GOTO ────────────────────────────────────────────────────
    goto_lines = "{\n"
    for estado_id, transiciones in sorted(tabla_goto.items()):
        goto_lines += f"    {estado_id}: {repr(transiciones)},\n"
    goto_lines += "}"

    # ── Serializar producciones (para mostrar en pasos) ────────────────────
    prods_lines = "[\n"
    for prod in todas_prods:
        prods_lines += f"    ({repr(prod.cabeza)}, {repr(tuple(prod.cuerpo))}),\n"
    prods_lines += "]"

    ignorados_repr = repr(set(tokens_ignorados))

    # ── Código del parser ──────────────────────────────────────────────────
    codigo = f"""\
# =============================================================
# ANALIZADOR SINTÁCTICO SLR — GENERADO AUTOMÁTICAMENTE
# Este archivo es INDEPENDIENTE del generador.
# =============================================================

TABLA_ACTION = {action_lines}

TABLA_GOTO = {goto_lines}

PRODUCCIONES = {prods_lines}

TOKENS_IGNORADOS = {ignorados_repr}


def _tipo_token(accion: str) -> str:
    \"\"\"
    Extrae el nombre del tipo de token de la acción producida por el lexer.
    Ejemplos:  'return INT' -> 'INT',   'INT' -> 'INT'
    \"\"\"
    accion = accion.strip()
    partes = accion.split()
    if not partes:
        return accion
    if partes[0].lower() == "return" and len(partes) > 1:
        return partes[1]
    return partes[-1]


def parsear(tokens_lexer: list):
    \"\"\"
    Ejecuta el análisis sintáctico SLR.

    Parámetros
    ----------
    tokens_lexer : list[(lexema, accion)]  — salida de scanner_generado.escanear()

    Retorna
    -------
    (exito: bool, pasos: list[str], errores: list[str])
    \"\"\"
    pasos = []
    errores = []

    # Filtrar tokens ignorados; acumular errores léxicos sin detener el análisis
    tokens = []
    for lexema, accion in tokens_lexer:
        if "ERROR" in accion.upper():
            errores.append(f"ERROR LÉXICO: símbolo no reconocido '{{lexema}}'")
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
    pasos.append(f"{{'Pila':<{{col_p}}}} {{'Entrada':<{{col_e}}}} Acción")
    pasos.append("-" * (col_p + col_e + 20))

    while True:
        estado = pila[-1]
        lexema, tipo = tokens[idx]

        pila_str  = " ".join(str(s) for s in pila)
        entr_str  = " ".join(t for _, t in tokens[idx : idx + 6])
        if len(tokens) - idx > 6:
            entr_str += " …"

        if estado not in TABLA_ACTION or tipo not in TABLA_ACTION[estado]:
            esperados = sorted(TABLA_ACTION.get(estado, {{}}).keys())
            msg = (
                f"ERROR SINTÁCTICO: token inesperado '{{lexema}}' "
                f"(tipo {{tipo}}) en estado {{estado}}. "
                f"Se esperaba: {{esperados}}"
            )
            pasos.append(f"{{pila_str:<{{col_p}}}} {{entr_str:<{{col_e}}}} ERROR")
            errores.append(msg)
            return False, pasos, errores

        accion = TABLA_ACTION[estado][tipo]
        tipo_acc = accion[0]

        if tipo_acc == "shift":
            j = accion[1]
            pasos.append(f"{{pila_str:<{{col_p}}}} {{entr_str:<{{col_e}}}} Desplazar '{{lexema}}' → s{{j}}")
            pila.append(j)
            idx += 1

        elif tipo_acc == "reduce":
            cabeza, cuerpo = accion[1], accion[2]
            prod_str = f"{{cabeza}} → {{' '.join(cuerpo) if cuerpo else 'ε'}}"
            pasos.append(f"{{pila_str:<{{col_p}}}} {{entr_str:<{{col_e}}}} Reducir {{prod_str}}")

            if cuerpo:
                pila = pila[: -len(cuerpo)]

            top = pila[-1]
            if top not in TABLA_GOTO or cabeza not in TABLA_GOTO[top]:
                errores.append(
                    f"ERROR SINTÁCTICO: no hay GOTO[{{top}}, {{cabeza}}]"
                )
                return False, pasos, errores

            pila.append(TABLA_GOTO[top][cabeza])

        elif tipo_acc == "accept":
            pasos.append(f"{{pila_str:<{{col_p}}}} {{entr_str:<{{col_e}}}} ACEPTAR ✓")
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
"""

    with open(ruta_salida, "w", encoding="utf-8") as f:
        f.write(codigo)

    return ruta_salida
