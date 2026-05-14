"""
Lector de archivos YAPar (.yalp).
Formato basado en Consideraciones de YAPar (UVG CC3071 2026).

Secciones:
  1. Tokens: %token TOKEN1 TOKEN2 ... / IGNORE TOKEN
  2. Separador: %%
  3. Producciones: name: body1 | body2 ;
"""


class ErrorYAPar(Exception):
    pass


def _eliminar_comentarios(texto: str) -> str:
    """Elimina bloques /* ... */ sin usar librería re."""
    resultado = []
    i = 0
    n = len(texto)
    while i < n:
        if texto[i:i+2] == "/*":
            fin = texto.find("*/", i + 2)
            if fin == -1:
                break
            i = fin + 2
        else:
            resultado.append(texto[i])
            i += 1
    return "".join(resultado)


def _es_cabecera_produccion(linea: str) -> bool:
    """Devuelve True si la línea comienza con  nombre: (sin ser una alternativa |)."""
    if linea.startswith("|"):
        return False
    if ":" not in linea:
        return False
    nombre = linea.split(":", 1)[0].strip()
    if not nombre:
        return False
    if not (nombre[0].isalpha() or nombre[0] == "_"):
        return False
    return all(c.isalnum() or c == "_" for c in nombre)


class LectorYAPar:

    def __init__(self):
        self.tokens_declarados = []
        self.tokens_ignorados  = set()
        self.producciones      = []
        self.simbolo_inicio    = None

    # ── API pública ─────────────────────────────────────────────────────────

    def parsear_archivo(self, ruta: str) -> "LectorYAPar":
        with open(ruta, "r", encoding="utf-8") as f:
            return self.parsear_texto(f.read())

    def parsear_texto(self, contenido: str) -> "LectorYAPar":
        self.tokens_declarados = []
        self.tokens_ignorados  = set()
        self.producciones      = []
        self.simbolo_inicio    = None

        contenido = _eliminar_comentarios(contenido)

        if "%%" not in contenido:
            raise ErrorYAPar("No se encontró el separador '%%' entre secciones.")

        sec_tokens, sec_prods = contenido.split("%%", 1)
        self._parsear_tokens(sec_tokens)
        self._parsear_producciones(sec_prods)
        return self

    # ── Conversión a Gramatica ───────────────────────────────────────────────

    def obtener_gramatica(self):
        from gramatica.grammar import Gramatica

        g = Gramatica()
        for t in self.tokens_declarados:
            g.terminales.add(t)

        primera = True
        for cabeza, _ in self.producciones:
            g.no_terminales.add(cabeza)
            if primera:
                g.simbolo_inicio = cabeza
                primera = False

        for cabeza, alternativas in self.producciones:
            for cuerpo in alternativas:
                g.agregar_produccion(cabeza, cuerpo)

        return g

    # ── Parseo interno ───────────────────────────────────────────────────────

    def _parsear_tokens(self, texto: str):
        for linea in texto.splitlines():
            linea = linea.strip()
            if not linea:
                continue
            if linea.lower().startswith("%token"):
                for t in linea[6:].split():
                    t = t.strip()
                    if t:
                        self.tokens_declarados.append(t)
            elif linea.upper().startswith("IGNORE"):
                for t in linea[6:].split():
                    t = t.strip()
                    if t:
                        self.tokens_ignorados.add(t)

    def _parsear_producciones(self, texto: str):
        cabeza_actual = None
        alternativas  = []

        for linea in texto.splitlines():
            linea = linea.strip()
            if not linea:
                continue

            if linea == ";":
                if cabeza_actual is not None:
                    self._registrar(cabeza_actual, alternativas)
                cabeza_actual = None
                alternativas  = []
                continue

            if _es_cabecera_produccion(linea):
                if cabeza_actual is not None:
                    self._registrar(cabeza_actual, alternativas)
                partes = linea.split(":", 1)
                cabeza_actual = partes[0].strip()
                alternativas  = []
                resto = partes[1].strip() if len(partes) > 1 else ""
                if resto:
                    alternativas.append(resto.split())
                continue

            if linea.startswith("|"):
                cuerpo = linea[1:].strip()
                alternativas.append(cuerpo.split() if cuerpo else [])
                continue

            if cabeza_actual is not None:
                alternativas.append(linea.split())

        if cabeza_actual is not None and alternativas:
            self._registrar(cabeza_actual, alternativas)

    def _registrar(self, cabeza: str, alternativas: list):
        if not alternativas:
            return
        if self.simbolo_inicio is None:
            self.simbolo_inicio = cabeza
        self.producciones.append((cabeza, [list(a) for a in alternativas]))
