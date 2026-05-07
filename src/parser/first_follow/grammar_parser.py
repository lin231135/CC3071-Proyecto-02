"""
Parsea una Gramática Libre de Contexto en formato de flecha simple.

Formato aceptado:
    E -> E PLUS T | T
    T -> T TIMES F | F
    F -> LPAREN E RPAREN | ID | epsilon

Reglas:
  - Cada línea define una o más alternativas para un no terminal.
  - El separador de alternativas es '|'.
  - 'epsilon' representa la producción vacía (A → ε).
  - Las líneas que comienzan con '#' son comentarios y se ignoran.
  - Los no terminales son los símbolos que aparecen como cabeza de producción.
  - Todo lo demás es un terminal.
  - El primer no terminal declarado es el símbolo inicial.
"""

from .grammar import Gramatica, EPSILON


class ErrorGramatica(Exception):
    """Error al parsear la gramática ingresada."""
    pass


class ParserGramatica:

    def parsear(self, texto: str) -> Gramatica:
        texto = self._limpiar(texto)
        return self._parsear(texto)

    # Limpieza 

    def _limpiar(self, texto: str) -> str:
        """Elimina líneas de comentario (# ...) y líneas vacías."""
        lineas = []
        for linea in texto.splitlines():
            sin_comentario = linea.split('#')[0].strip()
            if sin_comentario:
                lineas.append(sin_comentario)
        return '\n'.join(lineas)

    # Parseo

    def _parsear(self, texto: str) -> Gramatica:
        gramatica = Gramatica()

        # Primera pasada: recolectar todos los no terminales (cabezas de producción)
        for linea in texto.splitlines():
            if '->' not in linea:
                continue
            cabeza = linea.split('->')[0].strip()
            if cabeza:
                gramatica.no_terminales.add(cabeza)

        if not gramatica.no_terminales:
            raise ErrorGramatica(
                "No se encontraron producciones.\n"
                "Use el formato:  A -> B C | D"
            )

        # Segunda pasada: parsear cada producción
        primera = True
        for linea in texto.splitlines():
            if '->' not in linea:
                continue

            cabeza, resto = linea.split('->', 1)
            cabeza = cabeza.strip()

            if cabeza not in gramatica.no_terminales:
                continue

            if primera:
                gramatica.simbolo_inicio = cabeza
                primera = False

            for alternativa in resto.split('|'):
                simbolos = alternativa.strip().split()
                gramatica.agregar_produccion(cabeza, self._resolver_epsilon(simbolos))

        # Inferir terminales: todo símbolo en un cuerpo que no sea no terminal
        for prod in gramatica.producciones:
            for simbolo in prod.cuerpo:
                if simbolo not in gramatica.no_terminales:
                    gramatica.terminales.add(simbolo)

        return gramatica

    # Auxiliares

    @staticmethod
    def _resolver_epsilon(simbolos: list) -> list:
        """Convierte las palabras clave de epsilon en cuerpo vacío."""
        if simbolos in (['epsilon'], ['eps'], ['ε'], ['EPSILON']):
            return []
        return simbolos
