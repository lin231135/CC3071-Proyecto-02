"""
Proyecto 02 — Generador de Analizadores Sintácticos SLR
Interfaz gráfica principal en CustomTkinter.

Flujo de trabajo:
  1. Cargar .yal  → genera scanner_generado.py + visualiza AFD léxico
  2. Cargar .yalp → valida tokens, construye LR(0), genera parser_generado.py
                    + visualiza autómata LR(0)
  3. Cargar archivo de entrada → ejecuta lexer + parser, muestra pasos / errores
"""

import sys
import os
import importlib.util

import tkinter as tk
import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image

from lexico              import (LectorYALex, formatear_regex, infijo_a_postfijo,
                                  ArbolSintactico, generar_afd, minimizar_afd,
                                  generar_scanner_independiente)
from sintactico          import (LectorYAPar, ErrorYAPar, construir_tabla_slr,
                                  generar_parser_independiente, validar_tokens)
from visualizacion       import generar_imagen_afd, generar_imagen_lr0

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

C_BG     = "#1e1e1e"
C_SIDE   = "#333333"
C_GREEN  = "#00ff00"
C_RED    = "#ff4d4d"


class App(ctk.CTk):

    def __init__(self):
        super().__init__()
        self.title("Generador de Analizadores Sintácticos SLR  |  CC3071 UVG 2026")
        self.geometry("1400x820")
        self.minsize(1100, 650)

        self._lector_yalex = None
        self._lector_yapar = None
        self._afd_min      = None
        self._estados_lr0  = None
        self._ruta_scanner = None
        self._ruta_parser  = None

        self._construir_ui()

    # ======================================================================
    # Construcción de la interfaz
    # ======================================================================

    def _construir_ui(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self._construir_sidebar()

        self._f_gen   = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self._f_parse = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self._f_lex   = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")

        self._vista_generador()
        self._vista_parser()
        self._vista_lexer()

        self._ir_a(self._f_gen, self._btn_gen, self._btn_par, self._btn_lex)

    # Sidebar

    def _construir_sidebar(self):
        sb = ctk.CTkFrame(self, width=210, corner_radius=0, fg_color=C_SIDE)
        sb.grid(row=0, column=0, sticky="nsew")
        sb.grid_rowconfigure(5, weight=1)

        ctk.CTkLabel(
            sb,
            text="Compiladores\nCC3071 – UVG 2026",
            font=ctk.CTkFont("Segoe UI", 15, "bold"),
        ).grid(row=0, column=0, padx=20, pady=(22, 18))

        self._btn_gen = ctk.CTkButton(
            sb, text="⚙  Generador SLR",
            command=lambda: self._ir_a(self._f_gen, self._btn_gen,
                                       self._btn_par, self._btn_lex),
        )
        self._btn_gen.grid(row=1, column=0, padx=14, pady=5, sticky="ew")

        self._btn_par = ctk.CTkButton(
            sb, text="▶  Ejecutar Parser",
            command=lambda: self._ir_a(self._f_parse, self._btn_par,
                                       self._btn_gen, self._btn_lex),
            fg_color="transparent", border_width=1,
        )
        self._btn_par.grid(row=2, column=0, padx=14, pady=5, sticky="ew")

        self._btn_lex = ctk.CTkButton(
            sb, text="🔤  Analizador Léxico",
            command=lambda: self._ir_a(self._f_lex, self._btn_lex,
                                       self._btn_gen, self._btn_par),
            fg_color="transparent", border_width=1,
        )
        self._btn_lex.grid(row=3, column=0, padx=14, pady=5, sticky="ew")

        self._lbl_yal         = self._mk_estado(sb, row=6,  texto="YALex: —")
        self._lbl_yalp        = self._mk_estado(sb, row=7,  texto="YAPar: —")
        self._lbl_entrada     = self._mk_estado(sb, row=8,  texto="Entrada (parser): —")
        self._lbl_lex_entrada = self._mk_estado(sb, row=9,  texto="Entrada (lexer): —")

    def _mk_estado(self, padre, row, texto):
        lbl = ctk.CTkLabel(padre, text=texto, text_color="gray55",
                           font=ctk.CTkFont("Segoe UI", 10),
                           wraplength=182, anchor="w")
        lbl.grid(row=row, column=0, padx=12, pady=2, sticky="w")
        return lbl

    def _ir_a(self, activa, btn_activo, *otros):
        for f in (self._f_gen, self._f_parse, self._f_lex):
            f.grid_forget()
        activa.grid(row=0, column=1, sticky="nsew", padx=8, pady=8)
        btn_activo.configure(fg_color=["#3B8ED0", "#1F6AA5"], border_width=0)
        for b in otros:
            b.configure(fg_color="transparent", border_width=1)

    # ======================================================================
    # Vista 1: Generador SLR
    # ======================================================================

    def _vista_generador(self):
        v = self._f_gen
        v.grid_rowconfigure(1, weight=1)
        v.grid_columnconfigure(0, weight=1)

        tb = ctk.CTkFrame(v, height=54, corner_radius=8)
        tb.grid(row=0, column=0, sticky="ew", pady=(0, 8))

        ctk.CTkButton(tb, text="📂 Cargar .yal",        width=140, command=self._cargar_yal ).pack(side="left", padx=8, pady=8)
        ctk.CTkButton(tb, text="📂 Cargar .yalp",       width=140, command=self._cargar_yalp).pack(side="left", padx=4, pady=8)
        ctk.CTkButton(tb, text="👁 Ver AFD Léxico",     width=150,
                      fg_color="#2b6cb0", hover_color="#2c5282",
                      command=self._ver_afd).pack(side="right", padx=6, pady=8)
        ctk.CTkButton(tb, text="👁 Ver Autómata LR(0)", width=165,
                      fg_color="#276749", hover_color="#1e4d35",
                      command=self._ver_lr0).pack(side="right", padx=4, pady=8)

        # PanedWindow horizontal: sash arrastrable entre log y tabla
        paned = tk.PanedWindow(
            v, orient=tk.HORIZONTAL,
            sashwidth=6, sashrelief="flat", sashpad=1,
            bg="#2a2a2a", handlesize=0,
        )
        paned.grid(row=1, column=0, sticky="nsew", padx=4, pady=(0, 4))

        # Panel izquierdo: registro de generación
        pnl_log = ctk.CTkFrame(paned, corner_radius=8)
        pnl_log.grid_rowconfigure(1, weight=1)
        pnl_log.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(pnl_log, text="🖥  Registro de generación",
                     font=ctk.CTkFont("Segoe UI", 13, "bold")).grid(
            row=0, column=0, sticky="w", padx=10, pady=(8, 4))
        self._log_gen_box = ctk.CTkTextbox(
            pnl_log, font=ctk.CTkFont("Consolas", 12),
            fg_color=C_BG, text_color=C_GREEN, wrap="none")
        self._log_gen_box.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 8))
        self._log_gen_box.insert("0.0", "Carga un archivo .yal para comenzar…\n")
        self._log_gen_box.configure(state="disabled")
        paned.add(pnl_log, minsize=200, stretch="always")

        # Panel derecho: tabla SLR
        pnl_tab = ctk.CTkFrame(paned, corner_radius=8)
        pnl_tab.grid_rowconfigure(1, weight=1)
        pnl_tab.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(pnl_tab, text="📋  Tabla SLR  (ACTION / GOTO)",
                     font=ctk.CTkFont("Segoe UI", 13, "bold")).grid(
            row=0, column=0, sticky="w", padx=10, pady=(8, 4))
        self._tabla_box = ctk.CTkTextbox(
            pnl_tab, font=ctk.CTkFont("Consolas", 9),
            fg_color=C_BG, text_color="#d4d4d4", wrap="none")
        self._tabla_box.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 8))
        self._tabla_box.configure(state="disabled")
        paned.add(pnl_tab, minsize=200, stretch="always")

