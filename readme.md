# Laboratorio 03 — Calculadora de PRIMERO y SIGUIENTE

**Curso:** CC3071 — Diseño de Lenguajes de Programación  
**Universidad:** Universidad del Valle de Guatemala  
**Docente:** Carlos Valdez  


---

## Descripción

Este programa implementa el cálculo de las funciones **PRIMERO** (*First*) y **SIGUIENTE** (*Follow*) a partir de una Gramática Libre de Contexto (GLC) ingresada por el usuario.

Las funciones PRIMERO y SIGUIENTE son herramientas fundamentales para la construcción de analizadores sintácticos predictivos (LL) y tablas de análisis sintáctico. El cálculo sigue el **Algoritmo 4.3 del Libro del Dragón** (Aho et al., §4.4.2).

El programa permite:
1. Ingresar una GLC de forma manual o cargando un archivo `.txt`.
2. Identificar automáticamente los símbolos **terminales** y **no terminales**.
3. Calcular los **conjuntos PRIMERO** de todos los no terminales.
4. Calcular los **conjuntos SIGUIENTE** de todos los no terminales.
5. Mostrar los resultados de forma clara y estructurada en la interfaz gráfica.

---

## Estructura del laboratorio

- `main.py`: Archivo principal para ejecutar la aplicación.
- `src/parser/first_follow/`: Módulos para el análisis de gramáticas y el cálculo de conjuntos FIRST y FOLLOW.
  - `grammar.py`: Definición y manejo de gramáticas.
  - `grammar_parser.py`: Parser de gramáticas.
  - `first_sets.py`: Cálculo de conjuntos FIRST.
  - `follow_sets.py`: Cálculo de conjuntos FOLLOW.
- `src/tests/grammars/`: Archivos de prueba de gramáticas.
- `ui/app.py`: Interfaz de usuario para el proyecto.

---



---

## Formato de entrada de gramáticas

Cada producción se escribe en una línea usando `->` como separador. Las alternativas se separan con `|`. Use `epsilon` (o `eps`, `ε`, `EPSILON`) para producciones vacías. Las líneas que comienzan con `#` son comentarios y se ignoran.

```
# Ejemplo — Expresiones aritméticas
E -> E PLUS T | T
T -> T TIMES F | F
F -> LPAREN E RPAREN | ID
```

```
# Ejemplo — Con producción vacía
S -> A B C
A -> a | epsilon
B -> b | epsilon
C -> c
```

**Reglas de clasificación de símbolos:**
- Son **no terminales** todos los símbolos que aparecen como cabeza de al menos una producción.
- Son **terminales** todos los demás símbolos que aparecen en los cuerpos de las producciones.
- El **símbolo inicial** es el no terminal de la primera producción declarada.

---

## Gramáticas de prueba incluidas

### Gramática 1 — Expresiones aritméticas (`grammar1.txt`)

```
E -> E PLUS T | T
T -> T TIMES F | F
F -> LPAREN E RPAREN | ID
```

| No terminal | PRIMERO | SIGUIENTE |
|---|---|---|
| E | `{ ID, LPAREN }` | `{ $, PLUS, RPAREN }` |
| T | `{ ID, LPAREN }` | `{ $, PLUS, RPAREN, TIMES }` |
| F | `{ ID, LPAREN }` | `{ $, PLUS, RPAREN, TIMES }` |

---

### Gramática 2 — No terminales anulables (`grammar2.txt`)

```
S -> A B C
A -> a | epsilon
B -> b | epsilon
C -> c
```

| No terminal | PRIMERO | SIGUIENTE |
|---|---|---|
| S | `{ a, b, c }` | `{ $ }` |
| A | `{ a, ε }` | `{ b, c }` |
| B | `{ b, ε }` | `{ c }` |
| C | `{ c }` | `{ $ }` |

---

### Gramática 3 — Sentencias con `else` opcional (`grammar3.txt`)

```
stmtlist   -> stmtlist stmt | stmt
stmt       -> IF expr THEN stmt elseclause | ID ASSIGN expr
elseclause -> ELSE stmt | epsilon
expr       -> ID
```

| No terminal | PRIMERO | SIGUIENTE |
|---|---|---|
| stmtlist | `{ ID, IF }` | `{ $, ID, IF }` |
| stmt | `{ ID, IF }` | `{ $, ELSE, ID, IF }` |
| elseclause | `{ ELSE, ε }` | `{ $, ELSE, ID, IF }` |
| expr | `{ ID }` | `{ $, ELSE, ID, IF, THEN }` |

---

## Detalles de implementación

### `grammar.py` — Estructuras de datos

Define las clases `Produccion` y `Gramatica` que representan formalmente una GLC como la tupla **G = (V, T, P, S)**.

### `grammar_parser.py` — Parser de gramáticas

Convierte el texto de entrada en un objeto `Gramatica`. Realiza dos pasadas: primero recolecta los no terminales (cabezas de producción) y luego infiere los terminales a partir de los cuerpos. Soporta múltiples alternativas en una misma línea.

### `first_sets.py` — Conjuntos PRIMERO

Implementa el cálculo de `PRIMERO(X)` para cada símbolo, siguiendo el **Algoritmo 4.3 del Libro del Dragón (§4.4.2)**:

- `PRIMERO(a) = {a}` para todo terminal `a`.
- Para cada no terminal `A`, se itera sobre sus producciones hasta alcanzar un **punto fijo**.
- Incluye la función auxiliar `primero_de_cadena` para calcular `PRIMERO(X₁ X₂ … Xₙ)`, propagando correctamente la anulabilidad (ε).

### `follow_sets.py` — Conjuntos SIGUIENTE

Implementa el cálculo de `SIGUIENTE(A)` para cada no terminal, aplicando las tres reglas del Libro del Dragón:

1. `$ ∈ SIGUIENTE(S)`, donde `S` es el símbolo inicial.
2. Si `A → αBβ`, entonces `PRIMERO(β) − {ε} ⊆ SIGUIENTE(B)`.
3. Si `A → αB` o si `ε ∈ PRIMERO(β)`, entonces `SIGUIENTE(A) ⊆ SIGUIENTE(B)`.

El cálculo también itera hasta **punto fijo**.

### `app.py` — Interfaz gráfica

Construida con **CustomTkinter** en modo oscuro. Incluye botones de acceso rápido para cargar dos gramáticas de ejemplo, abrir archivos `.txt` desde disco y limpiar el área de trabajo. Los resultados se muestran formateados con separadores visuales e indicando claramente cada conjunto.

---

## Restricciones cumplidas

-  No se utilizaron librerías que calculen automáticamente PRIMERO o SIGUIENTE.
-  Todos los algoritmos fueron implementados manualmente desde cero.
-  El programa identifica terminales y no terminales de forma automática.
-  La interfaz gráfica muestra los resultados de forma clara y estructurada.
-  Se incluyen gramáticas de prueba de distinta complejidad.

---

## Video de ejecución

[![Ver demo en YouTube](https://img.youtube.com/vi/DHuI9BV_FEA/maxresdefault.jpg)](https://youtu.be/DHuI9BV_FEA)

>  **[Ver video en YouTube]([https://youtu.be/ENLACE_AQUI](https://youtu.be/DHuI9BV_FEA?si=Pm7BT1Gzz2lCvFpb))**

El video (≤ 5 minutos) muestra:

1. La ejecución del programa.
2. El ingreso de **dos gramáticas distintas** y, para cada una:
   - Identificación de los símbolos terminales y no terminales.
   - Conjuntos PRIMERO de todos los no terminales.
   - Conjuntos SIGUIENTE de todos los no terminales.

---

## Autores

| Nombre | Carné |
|---|---|
| *Javier Linares* | *231135* |
| *Gadiel Ocaña* | *231270* |
| *Cindy Gualim* | *21226* |

---

*Universidad del Valle de Guatemala — Facultad de Ingeniería — CC3071, 2026 I*