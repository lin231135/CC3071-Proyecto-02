from .modelos.nodo import Nodo

class ArbolSintactico:
    """Construye el árbol binario y calcula anulable, primera_pos, ultima_pos y siguiente_pos."""
    def __init__(self, regex_postfija, lista_acciones=None):
        self.regex = regex_postfija
        self.acciones = lista_acciones if lista_acciones else []
        self.raiz = None
        self.siguiente_pos = {}
        self.hojas = {}
        self.acciones_pos = {}
        self.contador_pos = 1
        self.contador_reglas = 0
        self.construir_arbol()

    def construir_arbol(self):
        pila = []
        for char in self.regex:
            if char in {'*', '+', '?'}:
                nodo = Nodo(char)
                nodo.hijo_izq = pila.pop()
                pila.append(nodo)
            elif char in {'.', '|'}:
                nodo = Nodo(char)
                nodo.hijo_der = pila.pop()
                nodo.hijo_izq = pila.pop()
                pila.append(nodo)
            else:
                if char == 'ε':
                    nodo = Nodo(char)
                else:
                    accion_actual = None
                    if char == '#':
                        if self.contador_reglas < len(self.acciones):
                            accion_actual = self.acciones[self.contador_reglas]
                            self.contador_reglas += 1

                    mapa_inverso = {'þ': '+', 'ÿ': '*', 'ß': '?', 'æ': '|', 'ð': '(', 'ñ': ')', 'ø': '.'}
                    char_real = mapa_inverso.get(char, char)

                    nodo = Nodo(char_real, self.contador_pos, accion_actual)
                    self.siguiente_pos[self.contador_pos] = set()
                    self.hojas[self.contador_pos] = char_real

                    if accion_actual:
                        self.acciones_pos[self.contador_pos] = accion_actual

                    self.contador_pos += 1
                pila.append(nodo)

        self.raiz = pila.pop()
        self.calcular_propiedades(self.raiz)

    def calcular_propiedades(self, nodo):
        """Recorre el árbol en Post-Orden (hijos primero, luego padre)."""
        if not nodo: return
        self.calcular_propiedades(nodo.hijo_izq)
        self.calcular_propiedades(nodo.hijo_der)

        if nodo.hijo_izq is None and nodo.hijo_der is None:
            if nodo.valor == 'ε':
                nodo.anulable = True
            else:
                nodo.anulable = False
                nodo.primera_pos.add(nodo.id_posicion)
                nodo.ultima_pos.add(nodo.id_posicion)

        elif nodo.valor == '|':
            nodo.anulable = nodo.hijo_izq.anulable or nodo.hijo_der.anulable
            nodo.primera_pos = nodo.hijo_izq.primera_pos.union(nodo.hijo_der.primera_pos)
            nodo.ultima_pos = nodo.hijo_izq.ultima_pos.union(nodo.hijo_der.ultima_pos)

        elif nodo.valor == '.':
            nodo.anulable = nodo.hijo_izq.anulable and nodo.hijo_der.anulable
            nodo.primera_pos = nodo.hijo_izq.primera_pos.union(nodo.hijo_der.primera_pos) if nodo.hijo_izq.anulable else set(nodo.hijo_izq.primera_pos)
            nodo.ultima_pos = nodo.hijo_der.ultima_pos.union(nodo.hijo_izq.ultima_pos) if nodo.hijo_der.anulable else set(nodo.hijo_der.ultima_pos)
            for i in nodo.hijo_izq.ultima_pos:
                self.siguiente_pos[i].update(nodo.hijo_der.primera_pos)

        elif nodo.valor == '*':
            nodo.anulable = True
            nodo.primera_pos = set(nodo.hijo_izq.primera_pos)
            nodo.ultima_pos = set(nodo.hijo_izq.ultima_pos)
            for i in nodo.ultima_pos:
                self.siguiente_pos[i].update(nodo.primera_pos)

        elif nodo.valor == '+':
            nodo.anulable = nodo.hijo_izq.anulable
            nodo.primera_pos = set(nodo.hijo_izq.primera_pos)
            nodo.ultima_pos = set(nodo.hijo_izq.ultima_pos)
            for i in nodo.ultima_pos:
                self.siguiente_pos[i].update(nodo.primera_pos)

        elif nodo.valor == '?':
            nodo.anulable = True
            nodo.primera_pos = set(nodo.hijo_izq.primera_pos)
            nodo.ultima_pos = set(nodo.hijo_izq.ultima_pos)
