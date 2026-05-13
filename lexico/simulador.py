def simular_cadena(estados_afd, cadena):
    """Simula el recorrido de la cadena en el AFD (Algoritmo 3.18)"""
    mapa_estados = {est.id_estado: est for est in estados_afd}
    estado_actual = estados_afd[0] # Siempre iniciamos en el primer estado ('A')
    
    for char in cadena:
        if char in estado_actual.transiciones:
            id_siguiente = estado_actual.transiciones[char]
            estado_actual = mapa_estados[id_siguiente]
        else:
            return False # Se atascó, el símbolo no tiene transición
            
    return estado_actual.es_aceptacion