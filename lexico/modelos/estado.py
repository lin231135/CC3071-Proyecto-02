class EstadoAFD:
    """Representa un estado del Autómata Finito Determinista (AFD)."""
    def __init__(self, id_estado, posiciones):
        self.id_estado = id_estado          # Ej: 'S1', 'S2', 'S3'
        self.posiciones = set(posiciones)   # Conjunto de ID de posiciones del árbol
        self.es_aceptacion = False          # ¿Contiene el símbolo #?
        self.accion = None                  # Acción a retornar (YALex)
        self.transiciones = {}              # Diccionario: {simbolo: id_estado_destino}