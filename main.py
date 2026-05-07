"""
Punto de entrada — Laboratorio 03: Calculadora de PRIMERO y SIGUIENTE.
Ejecutar con:  python main.py
"""

import sys
import os

# Agrega la raíz del proyecto al path para que los imports funcionen
# desde cualquier directorio de trabajo.
ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from ui.app import App


def main():
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
