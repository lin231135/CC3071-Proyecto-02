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

    # ======================================================================
    # Vista 2: Ejecutar Parser
    # ======================================================================

    def _vista_parser(self):
        v = self._f_parse
        v.grid_rowconfigure(1, weight=1)
        v.grid_columnconfigure(0, weight=1)

        tb = ctk.CTkFrame(v, height=54, corner_radius=8)
        tb.grid(row=0, column=0, sticky="ew", pady=(0, 8))

        ctk.CTkButton(tb, text="📂 Cargar archivo de entrada", width=200,
                      command=self._cargar_entrada).pack(side="left", padx=8, pady=8)
        ctk.CTkButton(tb, text="▶ Ejecutar Parser", width=160,
                      fg_color="#b85a14", hover_color="#91450e",
                      command=self._ejecutar_parser).pack(side="left", padx=4, pady=8)

        # PanedWindow horizontal: sash arrastrable entre los dos paneles
        paned = tk.PanedWindow(
            v, orient=tk.HORIZONTAL,
            sashwidth=6, sashrelief="flat", sashpad=1,
            bg="#2a2a2a", handlesize=0,
        )
        paned.grid(row=1, column=0, sticky="nsew", padx=4, pady=(0, 4))

        # Panel izquierdo: editor de entrada
        pnl_edit = ctk.CTkFrame(paned, corner_radius=8)
        pnl_edit.grid_rowconfigure(1, weight=1)
        pnl_edit.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(pnl_edit, text="📝  Archivo de entrada",
                     font=ctk.CTkFont("Segoe UI", 13, "bold")).grid(
            row=0, column=0, sticky="w", padx=10, pady=(8, 4))
        self._editor = ctk.CTkTextbox(
            pnl_edit, font=ctk.CTkFont("Consolas", 13), wrap="none")
        self._editor.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 8))
        paned.add(pnl_edit, minsize=160, width=320, stretch="never")

        # Panel derecho: consola de pasos/errores
        pnl_out = ctk.CTkFrame(paned, corner_radius=8)
        pnl_out.grid_rowconfigure(1, weight=1)
        pnl_out.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(pnl_out, text="🖥  Pasos del análisis / Errores",
                     font=ctk.CTkFont("Segoe UI", 13, "bold")).grid(
            row=0, column=0, sticky="w", padx=10, pady=(8, 4))
        self._parser_out = ctk.CTkTextbox(
            pnl_out, font=ctk.CTkFont("Consolas", 11),
            fg_color=C_BG, text_color=C_GREEN, wrap="none")
        self._parser_out.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 8))
        self._parser_out.insert("0.0",
            "Genera el lexer y el parser primero (vista ⚙),\n"
            "luego carga un archivo de entrada y presiona ▶.\n")
        self._parser_out.configure(state="disabled")
        paned.add(pnl_out, minsize=300, stretch="always")

    # ======================================================================
    # Vista 3: Analizador Léxico
    # ======================================================================

    def _vista_lexer(self):
        v = self._f_lex
        v.grid_rowconfigure(1, weight=1)
        v.grid_columnconfigure(0, weight=1)

        # Toolbar
        tb = ctk.CTkFrame(v, height=54, corner_radius=8)
        tb.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        ctk.CTkButton(tb, text="📂 Cargar archivo de entrada", width=200,
                      command=self._cargar_entrada_lexer).pack(side="left", padx=8, pady=8)
        ctk.CTkButton(tb, text="▶ Ejecutar Lexer", width=150,
                      fg_color="#b85a14", hover_color="#91450e",
                      command=self._ejecutar_lexer).pack(side="left", padx=4, pady=8)

        # PanedWindow horizontal: sash arrastrable
        paned = tk.PanedWindow(
            v, orient=tk.HORIZONTAL,
            sashwidth=6, sashrelief="flat", sashpad=1,
            bg="#2a2a2a", handlesize=0,
        )
        paned.grid(row=1, column=0, sticky="nsew", padx=4, pady=(0, 4))

        # Panel izquierdo: editor de entrada del lexer
        pnl_ed = ctk.CTkFrame(paned, corner_radius=8)
        pnl_ed.grid_rowconfigure(1, weight=1)
        pnl_ed.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(pnl_ed, text="📄  Archivo de entrada (Léxico)",
                     font=ctk.CTkFont("Segoe UI", 13, "bold")).grid(
            row=0, column=0, sticky="w", padx=10, pady=(8, 4))
        self._lex_editor = ctk.CTkTextbox(
            pnl_ed, font=ctk.CTkFont("Consolas", 13), wrap="none")
        self._lex_editor.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 8))
        paned.add(pnl_ed, minsize=160, width=320, stretch="never")

        # Panel derecho: consola de salida del lexer
        pnl_out = ctk.CTkFrame(paned, corner_radius=8)
        pnl_out.grid_rowconfigure(1, weight=1)
        pnl_out.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(pnl_out, text="🖥  Consola — Tokens generados",
                     font=ctk.CTkFont("Segoe UI", 13, "bold")).grid(
            row=0, column=0, sticky="w", padx=10, pady=(8, 4))
        self._lex_out = ctk.CTkTextbox(
            pnl_out, font=ctk.CTkFont("Consolas", 12),
            fg_color=C_BG, text_color=C_GREEN, wrap="none")
        self._lex_out.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 8))
        self._lex_out.insert("0.0", "Carga un archivo y presiona ▶ Ejecutar Lexer…\n")
        self._lex_out.configure(state="disabled")
        paned.add(pnl_out, minsize=300, stretch="always")

    # Ayudante para paneles de texto

    def _panel_texto(self, padre, col, titulo, texto_inicial="", color_texto="#d4d4d4", font_size=12):
        pnl = ctk.CTkFrame(padre)
        pnl.grid(row=0, column=col, sticky="nsew",
                 padx=(0, 5) if col == 0 else (5, 0))
        pnl.grid_rowconfigure(1, weight=1)
        pnl.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(pnl, text=titulo,
                     font=ctk.CTkFont("Segoe UI", 13, "bold")).grid(
            row=0, column=0, sticky="w", padx=10, pady=(8, 4))
        box = ctk.CTkTextbox(pnl, font=ctk.CTkFont("Consolas", font_size),
                              fg_color=C_BG, text_color=color_texto, wrap="none")
        box.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 8))
        if texto_inicial:
            box.insert("0.0", texto_inicial)
            box.configure(state="disabled")
        return box

    # ======================================================================
    # Acciones: carga de archivos
    # ======================================================================

    def _cargar_yal(self):
        ruta = filedialog.askopenfilename(
            title="Seleccionar archivo YALex (.yal)",
            filetypes=[("YALex", "*.yal"), ("Todos", "*.*")],
        )
        if not ruta:
            return
        self._lbl_yal.configure(text=f"YALex: {os.path.basename(ruta)}", text_color=C_GREEN)
        self._log(f"[YALex] Compilando: {os.path.basename(ruta)}\n")

        try:
            self._lector_yalex = LectorYALex(ruta)
            rc, ac = "", []
            for i, (r, a) in enumerate(self._lector_yalex.rules):
                rc += f"({formatear_regex(r)})"
                rc += "|" if i < len(self._lector_yalex.rules) - 1 else ""
                ac.append(a)

            arbol  = ArbolSintactico(infijo_a_postfijo(rc), ac)
            orig   = generar_afd(arbol)
            self._afd_min = minimizar_afd(orig)

            ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self._ruta_scanner = os.path.join(ROOT, "scanner_generado.py")
            generar_scanner_independiente(self._afd_min, self._lector_yalex.rules,
                                          self._ruta_scanner)

            self._log(
                f"[YALex] AFD: {len(orig)} estados → {len(self._afd_min)} minimizados\n"
                f"[YALex] Scanner guardado: scanner_generado.py\n"
            )
        except Exception as e:
            import traceback
            self._log(f"[ERROR YALex] {e}\n{traceback.format_exc()}\n", error=True)

    def _cargar_yalp(self):
        if not self._lector_yalex:
            messagebox.showwarning("Atención", "Primero carga el archivo .yal.")
            return
        ruta = filedialog.askopenfilename(
            title="Seleccionar archivo YAPar (.yalp)",
            filetypes=[("YAPar", "*.yalp"), ("Todos", "*.*")],
        )
        if not ruta:
            return
        self._lbl_yalp.configure(text=f"YAPar: {os.path.basename(ruta)}", text_color=C_GREEN)
        self._log(f"\n[YAPar] Compilando: {os.path.basename(ruta)}\n")

        try:
            self._lector_yapar = LectorYAPar().parsear_archivo(ruta)

            errores_val = validar_tokens(self._lector_yapar, self._lector_yalex)
            if errores_val:
                for e in errores_val:
                    self._log(f"[VALIDACIÓN] {e}\n", error=True)
                messagebox.showerror("Error de validación",
                                     "Tokens del YAPar no encontrados en YALex:\n\n"
                                     + "\n".join(errores_val))
                return

            self._log(f"[VALIDACIÓN] Tokens OK: {self._lector_yapar.tokens_declarados}\n")

            gramatica = self._lector_yapar.obtener_gramatica()
            (self._estados_lr0, _aug,
             tabla_action, tabla_goto,
             conflictos, todas_prods) = construir_tabla_slr(gramatica)

            for c in conflictos:
                self._log(f"[CONFLICTO] {c}\n", error=True)

            self._log(
                f"[LR(0)] {len(self._estados_lr0)} estados en el autómata\n"
                f"[SLR]   Tablas ACTION/GOTO construidas\n"
            )
            self._mostrar_tabla_slr(tabla_action, tabla_goto, gramatica)

            ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self._ruta_parser = os.path.join(ROOT, "parser_generado.py")
            generar_parser_independiente(tabla_action, tabla_goto, todas_prods,
                                         self._lector_yapar.tokens_ignorados,
                                         self._ruta_parser)
            self._log("[SLR] Parser guardado: parser_generado.py\n")

        except ErrorYAPar as e:
            self._log(f"[ERROR YAPar] {e}\n", error=True)
        except Exception as e:
            import traceback
            self._log(f"[ERROR] {e}\n{traceback.format_exc()}\n", error=True)

    def _cargar_entrada(self):
        ruta = filedialog.askopenfilename(
            title="Seleccionar archivo de entrada",
            filetypes=[("Texto", "*.txt"), ("Todos", "*.*")],
        )
        if not ruta:
            return
        self._lbl_entrada.configure(
            text=f"Entrada (parser): {os.path.basename(ruta)}", text_color=C_GREEN)
        with open(ruta, "r", encoding="utf-8") as f:
            contenido = f.read()
        self._editor.delete("1.0", "end")
        self._editor.insert("1.0", contenido)

    def _cargar_entrada_lexer(self):
        ruta = filedialog.askopenfilename(
            title="Seleccionar archivo de entrada (Léxico)",
            filetypes=[("Texto", "*.txt"), ("Todos", "*.*")],
        )
        if not ruta:
            return
        self._lbl_lex_entrada.configure(
            text=f"Entrada (lexer): {os.path.basename(ruta)}", text_color=C_GREEN)
        with open(ruta, "r", encoding="utf-8") as f:
            contenido = f.read()
        self._lex_editor.delete("1.0", "end")
        self._lex_editor.insert("1.0", contenido)

    # ======================================================================
    # Acciones: ejecución
    # ======================================================================

    def _ejecutar_parser(self):
        if not self._ruta_scanner or not self._ruta_parser:
            messagebox.showwarning("Atención",
                                   "Primero genera el lexer y el parser (vista ⚙).")
            return
        texto = self._editor.get("1.0", "end-1c")
        if not texto.strip():
            messagebox.showwarning("Atención", "El editor de entrada está vacío.")
            return

        self._limpiar(self._parser_out)
        self._out("═" * 68 + "\n  ANÁLISIS SINTÁCTICO SLR\n" + "═" * 68 + "\n\n")

        try:
            scanner = self._mod(self._ruta_scanner, "scanner_generado")
            tokens_lex = scanner.escanear(texto)

            self._out("── Tokens léxicos ──────────────────────────────────────\n")
            for lex, acc in tokens_lex:
                if "ERROR" in acc.upper():
                    self._out(f"  '{lex}'  →  {acc}\n", error=True)
                else:
                    self._out(f"  '{lex}'  →  {acc}\n")
            self._out("\n")

            parser = self._mod(self._ruta_parser, "parser_generado")
            exito, pasos, errores = parser.parsear(tokens_lex)

            self._out("── Pasos del análisis ──────────────────────────────────\n")
            for p in pasos:
                self._out(p + "\n")

            if errores:
                self._out("\n── Errores ─────────────────────────────────────────────\n")
                for e in errores:
                    self._out(e + "\n", error=True)

            self._out("\n" + "═" * 68 + "\n")
            if exito:
                self._out("  ✓  ACEPTADO — entrada sintácticamente correcta\n", ok=True)
            else:
                self._out("  ✗  RECHAZADO — se encontraron errores\n", error=True)
            self._out("═" * 68 + "\n")

        except Exception as e:
            import traceback
            self._out(f"[ERROR] {e}\n{traceback.format_exc()}\n", error=True)

    def _ejecutar_lexer(self):
        if not self._ruta_scanner:
            messagebox.showwarning("Atención", "Primero carga el .yal en ⚙.")
            return
        texto = self._lex_editor.get("1.0", "end-1c")
        if not texto.strip():
            messagebox.showwarning("Atención", "El editor de entrada del léxico está vacío.")
            return

        self._limpiar(self._lex_out)
        self._lex_out.configure(state="normal")
        self._lex_out.tag_config("err", foreground=C_RED)
        self._lex_out.tag_config("sep", foreground="#555555")
        self._lex_out.tag_config("hdr", foreground="#d4d4d4")
        self._lex_out.configure(state="disabled")

        try:
            scanner = self._mod(self._ruta_scanner, "scanner_generado")
            tokens  = scanner.escanear(texto)

            self._escr(self._lex_out,
                       f"{'LEXEMA':<20} TOKEN\n{'─'*48}\n", "hdr")

            errores, total = 0, 0
            for lex, acc in tokens:
                total += 1
                es_error = "ERROR" in acc.upper()
                if es_error:
                    errores += 1
                tag = "err" if es_error else None
                self._escr(self._lex_out,
                           f"{repr(lex):<20} {acc}\n", tag)

            self._escr(self._lex_out, "─" * 48 + "\n", "sep")
            if errores:
                self._escr(self._lex_out,
                           f"{total} tokens  |  {errores} error(es) léxico(s)\n", "err")
            else:
                self._escr(self._lex_out,
                           f"{total} tokens  |  sin errores léxicos\n", "hdr")

        except Exception as e:
            import traceback
            self._escr(self._lex_out, f"[ERROR] {e}\n{traceback.format_exc()}\n", "err")

    # ======================================================================
    # Visualizaciones
    # ======================================================================

    def _ver_afd(self):
        if not self._afd_min:
            messagebox.showwarning("Atención", "Primero carga un archivo .yal.")
            return
        try:
            generar_imagen_afd(self._afd_min).show()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar el diagrama:\n{e}")

    def _ver_lr0(self):
        if not self._estados_lr0:
            messagebox.showwarning("Atención", "Primero carga un archivo .yalp.")
            return
        try:
            generar_imagen_lr0(self._estados_lr0).show()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar el diagrama LR(0):\n{e}")

    # ======================================================================
    # Tabla SLR en el panel de texto
    # ======================================================================

    def _mostrar_tabla_slr(self, tabla_action, tabla_goto, gramatica):
        self._tabla_box.configure(state="normal")
        self._tabla_box.delete("1.0", "end")

        terminales = sorted(gramatica.terminales) + ["$"]
        no_term    = sorted(gramatica.no_terminales)
        C = 10

        hdr  = f"{'St.':<4} | "
        hdr += " ".join(f"{t[:C-1]:<{C}}" for t in terminales)
        hdr += "  |  "
        hdr += " ".join(f"{nt[:C-1]:<{C}}" for nt in no_term)

        self._tabla_box.insert("end",
            " " * 7 + "ACTION" + " " * max(0, len(terminales) * (C + 1) - 12) + " GOTO\n"
            + hdr + "\n" + "─" * len(hdr) + "\n")

        for sid in sorted(tabla_action.keys()):
            fila = f"{sid:<4} | "
            for t in terminales:
                cell = tabla_action[sid].get(t)
                if   cell is None:         txt = ""
                elif cell[0] == "shift":   txt = f"s{cell[1]}"
                elif cell[0] == "reduce":  txt = f"r/{cell[1].cabeza}"
                elif cell[0] == "accept":  txt = "acc"
                else:                      txt = ""
                fila += f"{txt[:C-1]:<{C}} "
            fila += " |  "
            for nt in no_term:
                fila += f"{str(tabla_goto[sid].get(nt,'')):<{C}} "
            self._tabla_box.insert("end", fila + "\n")

        self._tabla_box.configure(state="disabled")

    # ======================================================================
    # Utilidades internas
    # ======================================================================

    def _mod(self, ruta: str, nombre: str):
        if nombre in sys.modules:
            del sys.modules[nombre]
        spec = importlib.util.spec_from_file_location(nombre, ruta)
        mod  = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    def _log(self, txt: str, error: bool = False):
        self._log_gen_box.tag_config("err", foreground=C_RED)
        self._escr(self._log_gen_box, txt, "err" if error else None)

    def _out(self, txt: str, error: bool = False, ok: bool = False):
        self._parser_out.tag_config("err", foreground=C_RED)
        self._parser_out.tag_config("ok",  foreground="#6a9955")
        self._escr(self._parser_out, txt, "err" if error else ("ok" if ok else None))

    def _escr(self, widget, txt: str, tag=None):
        widget.configure(state="normal")
        if tag:
            widget.insert("end", txt, tag)
        else:
            widget.insert("end", txt)
        widget.configure(state="disabled")
        widget.yview("end")

    def _limpiar(self, widget):
        widget.configure(state="normal")
        widget.delete("1.0", "end")
        widget.configure(state="disabled")
