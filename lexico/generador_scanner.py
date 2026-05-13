"""
Genera el archivo scanner_generado.py — analizador léxico independiente.
El archivo generado NO depende del generador; tiene la tabla DFA embebida.
"""

def generar_scanner_independiente(afd, reglas, ruta_salida="scanner_generado.py"):
    tabla_transiciones = "{\n"
    estados_aceptacion = "{\n"

    mapa_inverso = {'þ': '+', 'ÿ': '*', 'ß': '?', 'æ': '|', 'ð': '(', 'ñ': ')', 'ø': '.', '§': '#'}

    for estado in afd:
        trans_seguras = {mapa_inverso.get(c, c): d for c, d in estado.transiciones.items()}
        tabla_transiciones += f"    '{estado.id_estado}': {trans_seguras},\n"

        if estado.es_aceptacion and estado.accion:
            accion_limpia = estado.accion.replace('\n', ' ').replace('"', '\\"')
            estados_aceptacion += f"    '{estado.id_estado}': \"{accion_limpia}\",\n"

    tabla_transiciones += "}"
    estados_aceptacion += "}"
    estado_inicial = afd[0].id_estado

    codigo = f"""\
# ==========================================
# ANALIZADOR LÉXICO GENERADO AUTOMÁTICAMENTE
# ==========================================

TABLA_TRANSICIONES = {tabla_transiciones}
ESTADOS_ACEPTACION = {estados_aceptacion}
ESTADO_INICIAL = '{estado_inicial}'


def escanear(texto):
    tokens_encontrados = []
    avance = 0
    n = len(texto)

    while avance < n:
        estado_actual = ESTADO_INICIAL
        ultimo_estado_aceptacion = None
        pos_ultimo_aceptacion = -1

        i = avance
        while i < n:
            char = texto[i]
            if estado_actual in TABLA_TRANSICIONES and char in TABLA_TRANSICIONES[estado_actual]:
                estado_actual = TABLA_TRANSICIONES[estado_actual][char]
                if estado_actual in ESTADOS_ACEPTACION:
                    ultimo_estado_aceptacion = estado_actual
                    pos_ultimo_aceptacion = i
                i += 1
            else:
                break

        if ultimo_estado_aceptacion is not None:
            lexema = texto[avance : pos_ultimo_aceptacion + 1]
            accion  = ESTADOS_ACEPTACION[ultimo_estado_aceptacion]
            tokens_encontrados.append((lexema, accion))
            avance = pos_ultimo_aceptacion + 1
        else:
            char_error = texto[avance]
            if char_error.strip():
                tokens_encontrados.append(
                    (char_error, "ERROR LÉXICO: Símbolo no reconocido en el lenguaje")
                )
            avance += 1

    return tokens_encontrados


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r', encoding='utf-8') as f:
            contenido = f.read()
        for lexema, token in escanear(contenido):
            print(f"Lexema: '{{lexema}}' -> Accion: {{token}}")
    else:
        print("Uso: python scanner_generado.py archivo.txt")
"""

    with open(ruta_salida, "w", encoding="utf-8") as f:
        f.write(codigo)

    return ruta_salida
