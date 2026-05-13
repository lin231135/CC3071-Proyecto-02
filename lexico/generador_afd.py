from .modelos.estado import EstadoAFD

def generar_afd(arbol):
    estado_inicial_pos = frozenset(arbol.raiz.primera_pos)
    estado_inicial = EstadoAFD('S0', estado_inicial_pos)

    estados_creados = {estado_inicial_pos: estado_inicial}
    cola_sin_marcar = [estado_inicial_pos]

    alfabeto = set()
    posiciones_fin = set()
    for pos, char in arbol.hojas.items():
        if char == '#': posiciones_fin.add(pos)
        else: alfabeto.add(char)

    contador_estados = 1

    while cola_sin_marcar:
        T = cola_sin_marcar.pop(0)
        estado_actual = estados_creados[T]

        posiciones_aceptacion = [p for p in T if p in posiciones_fin]
        if posiciones_aceptacion:
            estado_actual.es_aceptacion = True
            pos_ganadora = min(posiciones_aceptacion)
            estado_actual.accion = arbol.acciones_pos.get(pos_ganadora)

        for char in alfabeto:
            U = set()
            for pos in T:
                if arbol.hojas[pos] == char:
                    U.update(arbol.siguiente_pos[pos])

            U_frozen = frozenset(U)
            if U_frozen:
                if U_frozen not in estados_creados:
                    nuevo_id = f"S{contador_estados}"
                    contador_estados += 1
                    nuevo_estado = EstadoAFD(nuevo_id, U_frozen)
                    estados_creados[U_frozen] = nuevo_estado
                    cola_sin_marcar.append(U_frozen)

                estado_actual.transiciones[char] = estados_creados[U_frozen].id_estado

    return list(estados_creados.values())
