"""
Valida que los tokens declarados en el archivo YAPar también estén
definidos como acciones en el archivo YALex generado.
"""


def _es_nombre_token(texto: str) -> bool:
    """True si el texto es un identificador en mayúsculas (TOKEN_NAME)."""
    if not texto:
        return False
    if not texto[0].isupper():
        return False
    return all(c.isupper() or c.isdigit() or c == "_" for c in texto)


def _tokens_en_accion(accion: str) -> list:
    """Divide la accion en palabras y devuelve las que son nombres de token."""
    tokens = []
    palabra = []
    for c in accion + " ":
        if c.isalnum() or c == "_":
            palabra.append(c)
        else:
            if palabra:
                w = "".join(palabra)
                if _es_nombre_token(w):
                    tokens.append(w)
            palabra = []
    return tokens


def _tokens_de_yalex(lector_yalex) -> set:
    """Extrae los nombres de tokens del objeto LectorYALex."""
    tokens = set()
    for _, accion in lector_yalex.rules:
        accion = accion.strip()
        if accion.lower().startswith("return "):
            partes = accion.split()
            if len(partes) >= 2:
                tokens.add(partes[1].strip())
            continue
        encontrados = _tokens_en_accion(accion)
        if encontrados:
            tokens.add(encontrados[-1])
    return tokens


def validar_tokens(lector_yapar, lector_yalex) -> list:
    """
    Verifica que cada token declarado en %token del YAPar tenga una acción
    correspondiente en el YALex.

    Retorna lista de mensajes de error (vacía si todo está bien).
    """
    tokens_yalex = _tokens_de_yalex(lector_yalex)
    errores = []

    for token in lector_yapar.tokens_declarados:
        if token not in tokens_yalex:
            errores.append(
                f"Token '{token}' declarado en YAPar no encontrado en YALex.\n"
                f"  Tokens disponibles en YALex: {sorted(tokens_yalex)}"
            )

    return errores
