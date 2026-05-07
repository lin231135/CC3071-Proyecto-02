"""
Prueba rápida sin interfaz gráfica.
Ejecutar con:  python tests/smoke_test.py
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.parser.first_follow import (
    ParserGramatica, calcular_primero, calcular_siguiente, EPSILON
)


def seccion(titulo):
    print(f"\n{'='*56}\n  {titulo}\n{'='*56}")


def mostrar(g, primero, siguiente):
    print(f"  Símbolo inicial  : {g.simbolo_inicio}")
    print(f"  No terminales    : {sorted(g.no_terminales)}")
    print(f"  Terminales       : {sorted(g.terminales)}")
    print()
    ancho = max(len(nt) for nt in g.no_terminales)
    for nt in sorted(g.no_terminales):
        print(f"  PRIMERO({nt:<{ancho}})   = {sorted(primero[nt])}")
    print()
    for nt in sorted(g.no_terminales):
        print(f"  SIGUIENTE({nt:<{ancho}}) = {sorted(siguiente[nt])}")


BASE = os.path.join(os.path.dirname(__file__), 'grammars')
parser = ParserGramatica()

for nombre in ['grammar1.txt', 'grammar2.txt', 'grammar3.txt']:
    texto = open(f"{BASE}/{nombre}", encoding='utf-8').read()
    g = parser.parsear(texto)
    p = calcular_primero(g)
    s = calcular_siguiente(g, p)
    seccion(nombre)
    mostrar(g, p, s)

print("\n  Todas las pruebas completadas.")
