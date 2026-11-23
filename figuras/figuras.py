"""Figuras del póster de Centinela (tercer corte, ruta B).

Datos: Tabla II del artículo «Centinela: diseño del mecanismo de alertas para llamadas simuladas».
Son DATOS SIMULADOS: 320 llamadas sintéticas (160 de riesgo y 160 legítimas), 16 familias ficticias,
umbral 1,15 y plazo de 4 s. IC 95 %: 4000 remuestreos de familias (semilla 20261117).
Paleta Okabe-Ito. Uso: python figuras.py  ->  fig1_diferencias.svg y fig2_conteos.svg
"""
import csv
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from pathlib import Path
for f in Path(__file__).resolve().parent.joinpath("fuentes").glob("*.ttf"):
    font_manager.fontManager.addfont(str(f))

AZUL, NARANJA, GRIS, TINTA = "#0072B2", "#E69F00", "#8A8F98", "#1B2230"
plt.rcParams.update({"font.family": "Montserrat", "font.size": 26, "svg.fonttype": "none",
                     "axes.edgecolor": GRIS, "axes.labelcolor": TINTA, "xtick.color": TINTA, "ytick.color": TINTA})

with open("datos_tabla_ii.csv", encoding="utf-8") as f:
    filas = list(csv.DictReader(f))
pp = lambda v: f"{v:+.1f}".replace(".", ",").replace("+", "+").replace("-", "−")

def sello(ax):
    ax.text(0.995, 1.02, "LLAMADAS INVENTADAS", transform=ax.transAxes, ha="right", va="bottom",
            fontsize=26, fontweight="bold", color="white",
            bbox=dict(boxstyle="round,pad=0.35", fc="#C0392B", ec="none"))

# Figura 1: diferencias C − F con IC 95 %
orden = ["Falsas alertas", "Avisos a tiempo", "Sensibilidad"]
nombre_simple = {"Falsas alertas": "Avisos falsos", "Avisos a tiempo": "Avisos a tiempo", "Sensibilidad": "Fraudes detectados"}
nota = {"Falsas alertas": "menos es mejor", "Avisos a tiempo": "más es mejor", "Sensibilidad": "más es mejor"}
fig, ax = plt.subplots(figsize=(18.5, 7.4))
for i, nombre in enumerate(orden):
    r = next(x for x in filas if x["medida"] == nombre)
    y = len(orden) - 1 - i
    d, lo, hi = float(r["dif_pp"]), float(r["ic_inf_pp"]), float(r["ic_sup_pp"])
    ax.plot([lo, hi], [y, y], color=AZUL, lw=7, solid_capstyle="round")
    ax.plot(d, y, "o", ms=26, color=AZUL, mec="white", mew=3)
    ax.text(0.8, y, f"de {r['F']} a {r['C']} de {r['n_clase']}\nmargen: {pp(lo)} a {pp(hi)}",
            va="center", ha="left", fontsize=26, color=TINTA, linespacing=1.25)
    ax.text(-20.6, y, f"{nombre_simple[nombre]}\n", ha="right", va="center", fontsize=26, fontweight="bold", color=TINTA)
    ax.text(-20.6, y - 0.18, f"({nota[nombre]})", ha="right", va="center", fontsize=24, color=GRIS)
ax.axvline(0, color=TINTA, lw=2)
ax.text(-0.4, -0.62, "sin cambio", fontsize=24, color=GRIS, va="bottom", ha="right")
ax.set_xlim(-20, 12); ax.set_ylim(-0.7, 2.7)
ax.set_yticks([]); ax.set_xticks(range(-20, 1, 5))
ax.set_xticklabels([pp(v).replace(",0", "") if v else "0" for v in range(-20, 1, 5)])
ax.set_xlabel("Cambio al recordar lo dicho (puntos de porcentaje)", fontsize=26, labelpad=12)
for s in ("top", "right", "left"): ax.spines[s].set_visible(False)
sello(ax)
fig.subplots_adjust(left=0.27, right=0.99, top=0.88, bottom=0.2)
fig.savefig("fig1_diferencias.svg"); fig.savefig("fig1_diferencias.png", dpi=150)

# Figura 2: conteos por regla, barras desde cero
fig, ax = plt.subplots(figsize=(18.5, 5.3))
w = 0.36
for i, nombre in enumerate(["Sensibilidad", "Avisos a tiempo", "Falsas alertas"]):
    r = next(x for x in filas if x["medida"] == nombre)
    for j, (regla, color) in enumerate((("F", NARANJA), ("C", AZUL))):
        v = int(r[regla]); x = i + (j - 0.5) * w
        ax.bar(x, v, w * 0.92, color=color)
        ax.text(x, v + 3, f"{v}", ha="center", va="bottom", fontsize=26, fontweight="bold", color=TINTA)
        if i == 0:
            ax.text(x, v / 2, "Solo lo\núltimo" if regla == "F" else "Recordando\nlo dicho", ha="center", va="center", fontsize=21,
                    fontweight="bold", color="white" if regla == "C" else TINTA, linespacing=1.1)
ax.set_xticks(range(3))
ax.set_xticklabels(["Fraudes detectados\n(de 160 con fraude)", "Avisos a tiempo\n(de 160 con fraude)", "Avisos falsos\n(de 160 normales)"])
ax.set_ylim(0, 160); ax.set_yticks([0, 40, 80, 120, 160]); ax.set_ylabel("Llamadas")
ax.yaxis.grid(True, color="#E3E6EB", lw=1); ax.set_axisbelow(True)
for s in ("top", "right"): ax.spines[s].set_visible(False)
sello(ax)
fig.subplots_adjust(left=0.08, right=0.99, top=0.86, bottom=0.3)
fig.savefig("fig2_conteos.svg"); fig.savefig("fig2_conteos.png", dpi=150)
print("listo")
