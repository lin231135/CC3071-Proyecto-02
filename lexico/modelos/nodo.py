class Nodo:
    """Representa un nodo dentro del árbol sintáctico de la expresión regular."""
    def __init__(self, valor, id_posicion=None, accion=None):
        self.valor = valor
        self.id_posicion = id_posicion # Solo las hojas (operandos) tienen ID
        self.accion = accion           # Guarda la acción de YALex
        self.hijo_izq = None
        self.hijo_der = None
        
        # Propiedades exigidas por el Algoritmo 3.36 (Libro del Dragón)
        self.anulable = False
        self.primera_pos = set()
        self.ultima_pos = set()