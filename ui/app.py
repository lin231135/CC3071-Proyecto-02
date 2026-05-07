"""
Laboratorio 03 — Calculadora de PRIMERO y SIGUIENTE
Interfaz gráfica en CustomTkinter.
"""

import sys
import os
from tkinter import filedialog, messagebox

import customtkinter as ctk

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.parser.first_follow.grammar_parser import ParserGramatica, ErrorGramatica
from src.parser.first_follow.first_sets import calcular_primero
from src.parser.first_follow.follow_sets import calcular_siguiente
from src.parser.first_follow.grammar import EPSILON, MARCA_FIN

# ── Tema 
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

EJEMPLO_1 = """\
# Gramática 1 — Expresiones aritméticas (Libro del Dragón §4.28)
E -> E PLUS T | T
T -> T TIMES F | F
F -> LPAREN E RPAREN | ID\
"""

EJEMPLO_2 = """\
# Gramática 2 — No terminales anulables (con epsilon)
S -> A B C
A -> a | epsilon
B -> b | epsilon
C -> c\
"""


class App(ctk.CTk):

    def __init__(self):
        super().__init__()
        self.title("Laboratorio 03 — PRIMERO y SIGUIENTE  |  CC3071 UVG 2026")
        self.geometry("1200x720")
        self.minsize(900, 580)
        self._construir_ui()

    # ── Construcción de la interfaz 

    def _construir_ui(self):
        self._construir_encabezado()

        cuerpo = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        cuerpo.pack(fill="both", expand=True, padx=14, pady=(6, 14))
        cuerpo.columnconfigure(0, weight=5)
        cuerpo.columnconfigure(1, weight=6)
        cuerpo.rowconfigure(0, weight=1)

        self._construir_panel_entrada(cuerpo)
        self._construir_panel_resultados(cuerpo)

    def _construir_encabezado(self):
        enc = ctk.CTkFrame(self, height=56, corner_radius=0)
        enc.pack(fill="x")
        enc.pack_propagate(False)

        ctk.CTkLabel(
            enc,
            text="Calculadora de PRIMERO y SIGUIENTE",
            font=ctk.CTkFont("Segoe UI", 19, "bold"),
        ).pack(side="left", padx=18, pady=10)

        ctk.CTkLabel(
            enc,
            text="CC3071 — UVG 2026",
            font=ctk.CTkFont("Segoe UI", 12),
            text_color="gray70",
        ).pack(side="right", padx=18)

    def _construir_panel_entrada(self, padre):
        marco = ctk.CTkFrame(padre)
        marco.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        marco.rowconfigure(2, weight=1)
        marco.columnconfigure(0, weight=1)

        # Barra superior
        barra = ctk.CTkFrame(marco, fg_color="transparent")
        barra.grid(row=0, column=0, sticky="ew", padx=12, pady=(12, 0))

        ctk.CTkLabel(
            barra,
            text="Gramática de entrada",
            font=ctk.CTkFont("Segoe UI", 14, "bold"),
        ).pack(side="left")

        for etiqueta, cmd in [
            ("Cargar .txt", self._cargar_archivo),
            ("Ejemplo 1",   self._ejemplo_1),
            ("Ejemplo 2",   self._ejemplo_2),
            ("Limpiar",     self._limpiar),
        ]:
            ctk.CTkButton(barra, text=etiqueta, width=95, height=28,
                          command=cmd).pack(side="right", padx=3)

        # Área de texto
        self._caja_entrada = ctk.CTkTextbox(
            marco, font=ctk.CTkFont("Courier New", 13), wrap="none"
        )
        self._caja_entrada.grid(row=2, column=0, sticky="nsew", padx=12, pady=(8, 4))

        # Indicación de formato
        ctk.CTkLabel(
            marco,
            text="Formato:  A -> B C | D      |      Use 'epsilon' para producciones vacías",
            font=ctk.CTkFont("Segoe UI", 10),
            text_color="gray55",
        ).grid(row=3, column=0, sticky="w", padx=13, pady=(0, 4))

        # Botón calcular
        ctk.CTkButton(
            marco,
            text="Calcular  PRIMERO  y  SIGUIENTE",
            font=ctk.CTkFont("Segoe UI", 14, "bold"),
            height=42,
            command=self._calcular,
        ).grid(row=4, column=0, sticky="ew", padx=12, pady=(2, 12))

    def _construir_panel_resultados(self, padre):
        marco = ctk.CTkFrame(padre)
        marco.grid(row=0, column=1, sticky="nsew")
        marco.rowconfigure(1, weight=1)
        marco.columnconfigure(0, weight=1)

        ctk.CTkLabel(
            marco,
            text="Resultados",
            font=ctk.CTkFont("Segoe UI", 14, "bold"),
        ).grid(row=0, column=0, sticky="w", padx=12, pady=(12, 4))

        self._caja_resultados = ctk.CTkTextbox(
            marco, font=ctk.CTkFont("Courier New", 13), state="disabled", wrap="none"
        )
        self._caja_resultados.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 12))

    # ── Acciones 

    def _cargar_archivo(self):
        ruta = filedialog.askopenfilename(
            title="Abrir gramática",
            filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")],
        )
        if not ruta:
            return
        try:
            with open(ruta, encoding="utf-8") as f:
                contenido = f.read()
            self._escribir_entrada(contenido)
        except OSError as e:
            messagebox.showerror("Error al abrir archivo", str(e))

    def _ejemplo_1(self):
        self._escribir_entrada(EJEMPLO_1)

    def _ejemplo_2(self):
        self._escribir_entrada(EJEMPLO_2)

    def _limpiar(self):
        self._escribir_entrada("")
        self._escribir_resultados("")

    def _calcular(self):
        texto = self._caja_entrada.get("1.0", "end").strip()
        if not texto:
            messagebox.showwarning("Entrada vacía", "Por favor ingrese una gramática.")
            return
        try:
            gramatica = ParserGramatica().parsear(texto)
            if not gramatica.producciones:
                raise ErrorGramatica("No se encontraron producciones en la gramática.")

            primero  = calcular_primero(gramatica)
            siguiente = calcular_siguiente(gramatica, primero)

            self._escribir_resultados(self._formatear(gramatica, primero, siguiente))

        except ErrorGramatica as e:
            messagebox.showerror("Error en la gramática", str(e))
        except Exception as e:
            messagebox.showerror("Error inesperado", f"{type(e).__name__}: {e}")

    # ── Formateo de resultados 

    def _formatear(self, gramatica, primero, siguiente) -> str:
        AN = "═" * 52
        SEP = lambda t: f"\n{AN}\n  {t}\n{AN}"

        lineas = [SEP("RESUMEN DE LA GRAMÁTICA")]
        lineas.append(f"  Símbolo inicial  : {gramatica.simbolo_inicio}")
        lineas.append(f"  No terminales    : {{{', '.join(sorted(gramatica.no_terminales))}}}")
        lineas.append(f"  Terminales       : {{{', '.join(sorted(gramatica.terminales))}}}")
        lineas.append("")
        lineas.append("  Producciones:")
        for prod in gramatica.producciones:
            cuerpo = ' '.join(prod.cuerpo) if prod.cuerpo else EPSILON
            lineas.append(f"    {prod.cabeza}  →  {cuerpo}")

        ancho = max(len(nt) for nt in gramatica.no_terminales) + 2

        lineas.append(SEP("CONJUNTOS PRIMERO"))
        for nt in sorted(gramatica.no_terminales):
            elementos = ', '.join(sorted(primero[nt]))
            lineas.append(f"  PRIMERO( {nt:<{ancho}})  =  {{ {elementos} }}")

        lineas.append(SEP("CONJUNTOS SIGUIENTE"))
        for nt in sorted(gramatica.no_terminales):
            elementos = ', '.join(sorted(siguiente[nt]))
            lineas.append(f"  SIGUIENTE( {nt:<{ancho}})  =  {{ {elementos} }}")

        lineas.append(f"\n{AN}")
        return '\n'.join(lineas)

    # ── Utilidades 

    def _escribir_entrada(self, texto: str):
        self._caja_entrada.delete("1.0", "end")
        self._caja_entrada.insert("1.0", texto)

    def _escribir_resultados(self, texto: str):
        self._caja_resultados.configure(state="normal")
        self._caja_resultados.delete("1.0", "end")
        self._caja_resultados.insert("1.0", texto)
        self._caja_resultados.configure(state="disabled")
