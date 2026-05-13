from .modelos.estado import EstadoAFD

def minimizar_afd(estados_afd):
    if not estados_afd: return []

    alfabeto = set()
    for e in estados_afd:
        alfabeto.update(e.transiciones.keys())
    alfabeto = sorted(list(alfabeto))

    mapa_estados = {e.id_estado: e for e in estados_afd}
    id_inicial_original = estados_afd[0].id_estado

    aceptacion = {e.id_estado for e in estados_afd if e.es_aceptacion}
    no_aceptacion = {e.id_estado for e in estados_afd if not e.es_aceptacion}

    particion = []
    if no_aceptacion: particion.append(no_aceptacion)

    grupos_acciones = {}
    for id_est in aceptacion:
        accion = mapa_estados[id_est].accion
        if accion not in grupos_acciones:
            grupos_acciones[accion] = set()
        grupos_acciones[accion].add(id_est)

    for grupo_acc in grupos_acciones.values():
        particion.append(grupo_acc)

    def obtener_grupo(id_est, particion_actual):
        for i, g in enumerate(particion_actual):
            if id_est in g: return i
        return -1

    while True:
        nueva_particion = []
        for grupo in particion:
            subgrupos = {}
            for id_est in grupo:
                estado = mapa_estados[id_est]
                firma = tuple(
                    obtener_grupo(estado.transiciones.get(simb), particion)
                    if estado.transiciones.get(simb) else -1
                    for simb in alfabeto
                )
                if firma not in subgrupos:
                    subgrupos[firma] = set()
                subgrupos[firma].add(id_est)
            nueva_particion.extend(subgrupos.values())

        if len(nueva_particion) == len(particion):
            break
        particion = nueva_particion

    particion.sort(key=lambda g: 0 if id_inicial_original in g else 1)

    estados_min = []
    mapa_nuevos_ids = {}
    contador = 0

    for grupo in particion:
        nuevo_id = f"M{contador}"
        contador += 1
        posiciones_combinadas = set()
        es_acept = False
        accion_grupo = None
        representante_id = list(grupo)[0]
        representante_obj = mapa_estados[representante_id]

        for id_est in grupo:
            est_obj = mapa_estados[id_est]
            posiciones_combinadas.update(est_obj.posiciones)
            if est_obj.es_aceptacion:
                es_acept = True
                accion_grupo = est_obj.accion
            mapa_nuevos_ids[id_est] = nuevo_id

        nuevo_estado = EstadoAFD(nuevo_id, posiciones_combinadas)
        nuevo_estado.es_aceptacion = es_acept
        nuevo_estado.accion = accion_grupo
        nuevo_estado._representante_temp = representante_obj
        estados_min.append(nuevo_estado)

    for est in estados_min:
        for simb, dest_original in est._representante_temp.transiciones.items():
            est.transiciones[simb] = mapa_nuevos_ids[dest_original]

    return estados_min
