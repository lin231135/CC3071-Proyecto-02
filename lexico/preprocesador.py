def escapar_regex(regex):
    """Disfraza los caracteres escapados con '\\' para que no sean tratados como operadores."""
    mapa_seguro = {'+': 'þ', '*': 'ÿ', '?': 'ß', '|': 'æ', '(': 'ð', ')': 'ñ', '.': 'ø', '\\': '\\'}
    resultado = ""
    i = 0
    while i < len(regex):
        if regex[i] == '\\' and i + 1 < len(regex):
            siguiente = regex[i+1]
            if siguiente in mapa_seguro:
                resultado += mapa_seguro[siguiente]
            else:
                resultado += siguiente
            i += 2
        else:
            resultado += regex[i]
            i += 1
    return resultado

def formatear_regex(regex):
    """Agrega concatenación explícita '.' y marcador '#'"""
    # 1. Escapar caracteres especiales primero
    regex = escapar_regex(regex)
    
    # 2. Lógica normal de concatenación explícita
    res = ""
    for i in range(len(regex)):
        c1 = regex[i]
        res += c1
        if i + 1 < len(regex):
            c2 = regex[i + 1]
            if c1 not in {'(', '|', '.'} and c2 not in {')', '|', '*', '+', '?', '.'}:
                res += '.'
    
    return f"({res}).#"

def infijo_a_postfijo(regex):
    """Algoritmo Shunting Yard para notación postfija."""
    precedencia = {'|': 1, '.': 2, '*': 3, '+': 3, '?': 3}
    salida = []
    pila = []
    
    for char in regex:
        if char.isalnum() or char == '#' or (char not in precedencia and char not in {'(', ')'}):
            salida.append(char)
        elif char == '(':
            pila.append(char)
        elif char == ')':
            while pila and pila[-1] != '(':
                salida.append(pila.pop())
            pila.pop()
        else:
            while pila and pila[-1] != '(' and precedencia.get(pila[-1], 0) >= precedencia.get(char, 0):
                salida.append(pila.pop())
            pila.append(char)
            
    while pila:
        salida.append(pila.pop())
        
    return "".join(salida)