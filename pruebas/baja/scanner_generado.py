# ==========================================
# ANALIZADOR LÉXICO GENERADO AUTOMÁTICAMENTE
# ==========================================

TABLA_TRANSICIONES = {
    'M0': {';': 'M5', 'f': 'M4', 'k': 'M4', 'G': 'M4', 'N': 'M4', '_': 'M4', 'D': 'M4', 'h': 'M4', '8': 'M6', 'a': 'M4', 'q': 'M4', '+': 'M7', '1': 'M6', 'Y': 'M4', 'u': 'M4', 'L': 'M4', 't': 'M2', 'j': 'M4', 'e': 'M4', 'n': 'M2', 'T': 'M4', 'y': 'M4', 'R': 'M4', 'r': 'M4', '2': 'M6', 'l': 'M4', 'M': 'M4', 'U': 'M4', 'V': 'M4', 'p': 'M4', 'S': 'M4', '=': 'M3', '6': 'M6', 'z': 'M4', 'I': 'M4', 'C': 'M4', 'X': 'M4', 'E': 'M4', 's': 'M4', 'v': 'M4', '9': 'M6', 'w': 'M4', 'F': 'M4', 'J': 'M4', 'O': 'M4', 'P': 'M4', 'W': 'M4', '7': 'M6', 'g': 'M4', 'H': 'M4', '3': 'M6', '0': 'M6', 'i': 'M4', '4': 'M6', 'o': 'M4', 'K': 'M4', 'A': 'M4', 'Q': 'M4', '5': 'M6', 'c': 'M4', 'Z': 'M4', 'B': 'M4', 'b': 'M4', 'm': 'M4', ' ': 'M1', 'd': 'M4', 'x': 'M4'},
    'M1': {},
    'M2': {'f': 'M4', 'k': 'M4', 'G': 'M4', 'N': 'M4', '_': 'M4', 'D': 'M4', 'h': 'M4', '8': 'M4', 'a': 'M4', 'q': 'M4', '1': 'M4', 'Y': 'M4', 'u': 'M4', 'L': 'M4', 't': 'M4', 'j': 'M4', 'e': 'M4', 'n': 'M4', 'T': 'M4', 'y': 'M4', 'R': 'M4', 'r': 'M4', '2': 'M4', 'l': 'M4', 'M': 'M4', 'U': 'M4', 'V': 'M4', 'p': 'M4', 'S': 'M4', '6': 'M4', 'z': 'M4', 'I': 'M4', 'C': 'M4', 'X': 'M4', 'E': 'M4', 's': 'M4', 'v': 'M4', '9': 'M4', 'w': 'M4', 'F': 'M4', 'J': 'M4', 'O': 'M4', 'P': 'M4', 'W': 'M4', '7': 'M4', 'g': 'M4', 'H': 'M4', '3': 'M4', '0': 'M4', 'i': 'M4', '4': 'M4', 'o': 'M4', 'K': 'M4', 'A': 'M4', 'Q': 'M4', '5': 'M4', 'c': 'M4', 'Z': 'M4', 'B': 'M4', 'b': 'M4', 'm': 'M4', 'd': 'M4', 'x': 'M4'},
    'M3': {},
    'M4': {'f': 'M4', 'k': 'M4', 'G': 'M4', 'N': 'M4', '_': 'M4', 'D': 'M4', 'h': 'M4', '8': 'M4', 'a': 'M4', 'q': 'M4', '1': 'M4', 'Y': 'M4', 'u': 'M4', 'L': 'M4', 't': 'M4', 'j': 'M4', 'e': 'M4', 'n': 'M4', 'T': 'M4', 'y': 'M4', 'R': 'M4', 'r': 'M4', '2': 'M4', 'l': 'M4', 'M': 'M4', 'U': 'M4', 'V': 'M4', 'p': 'M4', 'S': 'M4', '6': 'M4', 'z': 'M4', 'I': 'M4', 'C': 'M4', 'X': 'M4', 'E': 'M4', 's': 'M4', 'v': 'M4', '9': 'M4', 'w': 'M4', 'F': 'M4', 'J': 'M4', 'O': 'M4', 'P': 'M4', 'W': 'M4', '7': 'M4', 'g': 'M4', 'H': 'M4', '3': 'M4', '0': 'M4', 'i': 'M4', '4': 'M4', 'o': 'M4', 'K': 'M4', 'A': 'M4', 'Q': 'M4', '5': 'M4', 'c': 'M4', 'Z': 'M4', 'B': 'M4', 'b': 'M4', 'm': 'M4', 'd': 'M4', 'x': 'M4'},
    'M5': {},
    'M6': {'8': 'M6', '1': 'M6', '2': 'M6', '6': 'M6', '9': 'M6', '7': 'M6', '3': 'M6', '0': 'M6', '4': 'M6', '5': 'M6'},
    'M7': {},
}
ESTADOS_ACEPTACION = {
    'M1': "return WS",
    'M2': "return WS",
    'M3': "return ASSIGN",
    'M4': "return ID",
    'M5': "return SEMI",
    'M6': "return NUM",
    'M7': "return PLUS",
}
ESTADO_INICIAL = 'M0'


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
            print(f"Lexema: '{lexema}' -> Accion: {token}")
    else:
        print("Uso: python scanner_generado.py archivo.txt")
