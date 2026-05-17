# Proyecto 02 — Generador de Analizadores Sintácticos SLR

### Universidad del Valle de Guatemala — Diseño de Lenguajes de Programación 2026, I

* Cindy Gualim (21226)
* Javier Linares (231135)
* Gadiel Ocaña (231270)

---

Este proyecto implementa un **generador de analizadores sintácticos SLR(1)** de extremo a extremo. A partir de un archivo de especificación léxica (`.yal`) y un archivo de gramática libre de contexto (`.yalp`), el sistema construye automáticamente un analizador léxico y un analizador sintáctico totalmente funcionales, capaces de procesar texto plano e informar errores léxicos y sintácticos con precisión.

Todo el sistema fue construido desde cero, **sin utilizar ninguna librería de expresiones regulares**. El análisis léxico se resuelve mediante autómatas finitos y el análisis sintáctico mediante los algoritmos LR del Libro del Dragón.

---

## Características principales

* **Pipeline completo:** Lectura de `.yal` → AFD mínimo → `scanner_generado.py`; lectura de `.yalp` → colección canónica LR(0) → tablas SLR → `parser_generado.py`.
* **Analizadores independientes:** Los archivos generados (`scanner_generado.py` y `parser_generado.py`) son completamente autónomos; no importan ningún módulo del generador.
* **Recuperación de errores léxicos:** El scanner aplica la estrategia de pánico (Dragon Book §3.1.4): descarta el carácter inválido y continúa el análisis, reportando todos los errores de una sola pasada.
* **Detección de conflictos:** El generador identifica y reporta conflictos Shift/Reduce y Reduce/Reduce en la gramática.
* **Visualización de autómatas:** Diagramas en memoria con Graphviz del AFD léxico y del autómata LR(0), sin archivos temporales en disco.
* **Interfaz gráfica profesional:** Entorno tipo IDE con tres vistas independientes, paneles ajustables con barra divisora (sash), consola con colores de terminal y log de generación en tiempo real.

---

## Fundamentos teóricos y algoritmos

Todos los algoritmos están referenciados al **Libro del Dragón** (Aho, Lam, Sethi y Ullman, 2ª ed.).

### Analizador léxico

| Algoritmo | Referencia | Módulo |
|---|---|---|
| Shunting Yard (infijo → postfijo) | §3.4 | `lexico/preprocesador.py` |
| Cálculo de `anulable`, `primera_pos`, `ultima_pos`, `siguiente_pos` | §3.9.2 | `lexico/arbol_sintactico.py` |
| Construcción directa de AFD desde árbol sintáctico | §3.9.2, Alg. 3.36 | `lexico/generador_afd.py` |
| Minimización de estados (Hopcroft, con prioridad de reglas) | §3.9.4 | `lexico/minimizador_afd.py` |
| Maximal Munch en el scanner generado | §3.1.3 | `lexico/generador_scanner.py` |

### Analizador sintáctico

| Algoritmo | Referencia | Módulo |
|---|---|---|
| Conjuntos PRIMERO — punto fijo iterativo | §4.4.2, Alg. 4.3 | `gramatica/first_sets.py` |
| Conjuntos SIGUIENTE — punto fijo iterativo | §4.4.2, Alg. 4.3 | `gramatica/follow_sets.py` |
| Clausura de ítems LR(0) | §4.6.2, Alg. 4.38 | `sintactico/automata_lr0.py` |
| Función GOTO(I, X) | §4.6.2, Alg. 4.39 | `sintactico/automata_lr0.py` |
| Colección canónica de ítems LR(0) | §4.6.2, Alg. 4.40 | `sintactico/automata_lr0.py` |
| Construcción tablas SLR ACTION / GOTO | §4.6.2, Alg. 4.46 | `sintactico/tabla_slr.py` |

---

## Arquitectura del sistema

```
CC3071-Proyecto-02/
│
├── main.py                        # Punto de entrada — lanza la GUI
│
├── lexico/                        # Módulo del analizador léxico
│   ├── lector_yalex.py            # Parser del archivo .yal
│   ├── preprocesador.py           # Conversión infijo → postfijo
│   ├── arbol_sintactico.py        # Árbol sintáctico + funciones de posición
│   ├── generador_afd.py           # Construcción directa del AFD
│   ├── minimizador_afd.py         # Minimización de Hopcroft
│   └── generador_scanner.py      # Genera scanner_generado.py (independiente)
│
├── gramatica/                     # Estructuras de gramática + conjuntos
│   ├── grammar.py                 # Produccion, Gramatica (G = V, T, P, S)
│   ├── first_sets.py              # PRIMERO
│   └── follow_sets.py             # SIGUIENTE
│
├── sintactico/                    # Módulo del analizador sintáctico
│   ├── lector_yapar.py            # Parser del archivo .yalp (sin import re)
│   ├── automata_lr0.py            # Colección canónica LR(0)
│   ├── tabla_slr.py               # Tablas ACTION / GOTO
│   ├── validador.py               # Validación tokens YAPar ↔ YALex
│   └── generador_parser.py       # Genera parser_generado.py (independiente)
│
├── visualizacion/                 # Diagramas con Graphviz
│   ├── afd_lexico.py              # AFD del lexer → imagen PIL en memoria
│   └── automata_lr0.py            # Autómata LR(0) → imagen PIL en memoria
│
├── interfaz/
│   └── app.py                     # GUI CustomTkinter — 3 vistas
│
└── pruebas/                       # Conjuntos de prueba
    ├── baja/                      # Asignaciones con suma
    ├── media/                     # Expresiones aritméticas con precedencia
    └── alta/                      # Lenguaje imperativo: while, if, begin-end
```

---

## Interfaz gráfica

La aplicación tiene tres vistas accesibles desde el sidebar:

**Generador SLR**
Carga los archivos `.yal` y `.yalp`, valida que los tokens coincidan, construye el autómata LR(0), genera las tablas SLR y escribe los archivos `scanner_generado.py` y `parser_generado.py`. Muestra el log de generación y la tabla ACTION/GOTO completa en paneles ajustables.

**Ejecutar Parser**
Carga un archivo de texto plano y lo analiza con el lexer y parser generados. Muestra cada token reconocido, la secuencia completa de pasos Desplazar/Reducir y el veredicto final (ACEPTADO / RECHAZADO). Los errores léxicos y sintácticos se resaltan en rojo.

**Analizador Léxico**
Vista independiente del parser. Carga su propio archivo de entrada y ejecuta únicamente el scanner generado, mostrando la tabla de tokens con lexema y tipo. Demuestra la independencia modular del analizador léxico.

---

## Conjuntos de prueba

Cada nivel incluye cuatro archivos: lexer (`.yal`), gramática (`.yalp`), entrada válida y entrada con errores. También existe una versión **modificada** de la gramática con su propio par de entradas.

| Nivel | Gramática original | Modificación |
|---|---|---|
| **Baja** | Asignaciones con `+` | Agrega operador `-` (`MINUS`) |
| **Media** | Expresiones con `+`, `-`, `*`, `/`, paréntesis | Agrega instrucción `print(expr)` |
| **Alta** | `while`, `if-do`, `begin-end`, expresiones | Agrega rama `else` al `if` (sin conflictos S/R) |

La modificación `if-do-else` en alta complejidad es un caso teóricamente interesante: aunque el *dangling else* es un conflicto clásico en analizadores LL, en SLR(1) no genera conflicto porque `ELSE ∉ FOLLOW(if_stmt)`.

---

## Cómo ejecutar

```bash
# Instalar dependencias
pip install customtkinter pillow graphviz

# Ejecutar la aplicación
python main.py
```

> **Requisito:** Graphviz debe estar instalado en el sistema y disponible en el `PATH` para visualizar los diagramas de autómatas.

### Flujo de uso en la GUI

1. **Generador SLR** → `Cargar .yal` → `Cargar .yalp` → revisar log y tabla SLR
2. **Ejecutar Parser** → `Cargar archivo de entrada` → `Ejecutar Parser`
3. **Analizador Léxico** → `Cargar archivo de entrada` → `Ejecutar Lexer`
4. Usar `Ver AFD Léxico` y `Ver Autómata LR(0)` para visualizar los diagramas

---

## Restricciones cumplidas

| Restricción | Cumplimiento |
|---|---|
| Sin librerías de expresiones regulares | Verificado — `grep "import re"` retorna cero resultados |
| Scanner generado independiente del generador | `scanner_generado.py` solo contiene su tabla DFA embebida |
| Parser generado independiente del generador | `parser_generado.py` solo contiene tablas ACTION/GOTO embebidas |
| Interfaz gráfica amigable y estética | CustomTkinter, tema oscuro, paneles ajustables |
| Algoritmos SLR del Libro del Dragón | clausura, goto, colección canónica, FIRST/FOLLOW, ACTION/GOTO |
| Tres grupos de prueba (.yal + .yalp + válido + errores) | baja / media / alta, cada uno con versión original y modificada |

---

## Tecnologías utilizadas

* **Python 3.x**
* **CustomTkinter** — Interfaz gráfica
* **Graphviz** — Visualización de autómatas (AFD y LR(0))
* **Pillow** — Manipulación de imágenes en memoria
