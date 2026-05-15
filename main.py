"""
Proyecto 02 — Generador de Analizadores Sintácticos SLR
CC3071 Diseño de Lenguajes de Programación, UVG 2026

Ejecutar con:
    python main.py
"""

import sys
import os

ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from interfaz.app import App


def main():
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
