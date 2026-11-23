"""Regenera las figuras vectoriales a partir de las salidas sintéticas."""
from pathlib import Path
import csv
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from matplotlib.ticker import MultipleLocator

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "documento/figuras"
OUT.mkdir(parents=True, exist_ok=True)
STATS = json.loads((ROOT / "resultados/metricas_sinteticas.json").read_text())
CONF = json.loads((ROOT / "protocolo/configuracion.json").read_text())
with (ROOT / "datos/llamadas_sinteticas.csv").open(encoding="utf-8", newline="") as file:
    ROWS = list(csv.DictReader(file))

BLUE = "#156186"
ORANGE = "#AA4B18"
SLATE = "#283C4A"
STROKE = "#A6B9C7"
GRAY = "#607384"
plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 8, "pdf.fonttype": 42, "figure.dpi": 160,
    "text.color": SLATE, "axes.labelcolor": SLATE, "xtick.color": SLATE,
    "ytick.color": SLATE, "axes.edgecolor": STROKE,
})


def save(fig, name):
    fig.savefig(OUT / (name + ".pdf"), metadata={
        "Title": f"Centinela | {name}", "Author": "Centinela", "CreationDate": None, "ModDate": None,
    })
    plt.close(fig)


def scheme():
    fig, ax = plt.subplots(figsize=(3.48, 2.36))
    fig.subplots_adjust(left=.025, right=.975, top=.985, bottom=.018)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    def label(x, y, w, h, title, fill, col=SLATE, size=7.6):
        box = FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle="round,pad=0.012,rounding_size=0.016",
                             edgecolor=STROKE, linewidth=.65, facecolor=fill)
        ax.add_patch(box)
        ax.text(x, y, title, ha="center", va="center", color=col, fontsize=size, linespacing=1.15)

    def arrow(x, y, xx, yy):
        ax.annotate("", (xx, yy), (x, y), arrowprops=dict(arrowstyle="->", color=GRAY, lw=.8,
                    shrinkA=0, shrinkB=0))

    ax.text(.5, .96, "ENTRADAS PARA LA COMPARACIÓN", fontsize=7.3, weight="bold", ha="center")
    label(.245, .82, .445, .19, "Audio guionado\nWhisper y clasificador\n(estudio previsto)", "#F5F7F8", GRAY)
    label(.755, .82, .445, .19, "Trazas numéricas\nmodelo explícito\n(simulación ejecutada)", "#FDEFE6", ORANGE)
    arrow(.245, .71, .42, .62)
    arrow(.755, .71, .58, .62)
    label(.50, .55, .62, .11, "Evidencia por fragmento y tiempo", "#EAF4FA", BLUE)
    arrow(.42, .48, .245, .397)
    arrow(.58, .48, .755, .397)
    label(.245, .332, .40, .11, "F · Fragmento actual", "#FFFFFF")
    label(.755, .332, .40, .11, "C · Contexto previo", "#FFFFFF")
    arrow(.245, .258, .42, .175)
    arrow(.755, .258, .58, .175)
    label(.50, .095, .84, .135, "Primera alerta por llamada\nDetección · falsas alertas · demora", "#EAF4FA", BLUE)
    save(fig, "flujo")


def effects():
    fig, ax = plt.subplots(figsize=(3.48, 1.62))
    fig.subplots_adjust(left=.33, right=.975, bottom=.265, top=.79)
    fig.text(.5, .925, "Simulación · diferencia entre C y F", fontsize=8.3, ha="center", va="top", weight="bold")
    ax.axvline(0, linestyle=(0, (3, 2)), color=GRAY, lw=1)
    items = [
        ("sensibilidad", "Sensibilidad", "o", BLUE),
        ("oportunidad", "Aviso oportuno", "D", ORANGE),
        ("falsas_alertas", "Falsas alertas", "s", SLATE),
    ]
    for j, (metric, label, fmt, color) in enumerate(items):
        val = 100 * (STATS["principales"]["C"][metric] - STATS["principales"]["F"][metric])
        a, b = [100 * x for x in STATS["ic95_bootstrap"][metric]["C_menos_F"]]
        ax.errorbar(val, 2 - j, xerr=[[val - a], [b - val]], fmt=fmt, color=color,
                    capsize=3, elinewidth=1.25, markersize=4)
    ax.set_yticks([2, 1, 0], [label for _, label, _, _ in items], fontsize=7.45)
    ax.set_ylim(-.55, 2.55)
    ax.set_xlim(-20, 5)
    ax.xaxis.set_major_locator(MultipleLocator(5))
    ax.set_xlabel("Diferencia (puntos porcentuales)", fontsize=7.6, labelpad=2)
    ax.grid(axis="x", lw=.45, color="#E2E9ED")
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.tick_params(axis="y", length=0, pad=5)
    ax.tick_params(axis="x", length=2.5, labelsize=7.2)
    save(fig, "diferencias_sinteticas")


def coverage():
    positives = [r for r in ROWS if r["etiqueta"] == "1"]
    fig, ax = plt.subplots(figsize=(3.48, 1.8))
    fig.subplots_adjust(left=.168, right=.98, bottom=.28, top=.84)
    ax.set_title("Simulación · cobertura de avisos", fontsize=8.3, pad=7, weight="bold")
    for strat, name, color, style in (
        ("F", "F · Fragmento", BLUE, "-"),
        ("C", "C · Contexto", ORANGE, "--"),
    ):
        times = sorted(float(r[f"demora_{strat}_s"]) for r in positives
                       if r[f"demora_{strat}_s"] and 0 <= float(r[f"demora_{strat}_s"]) <= 4)
        ax.step([0, *times, 4], [0, *[100 * j / len(positives) for j in range(1, len(times) + 1)],
                                100 * len(times) / len(positives)], where="post", label=name,
                color=color, linestyle=style, lw=1.45)
    ax.set(xlim=(0, 4.05), ylim=(0, 55))
    ax.xaxis.set_major_locator(MultipleLocator(1))
    ax.set_yticks([0, 20, 40])
    ax.set_xlabel("Plazo desde fin de solicitud (s)", fontsize=7.4, labelpad=2)
    ax.set_ylabel("Cobertura (%)", fontsize=7.4, labelpad=2)
    ax.grid(axis="y", color="#E2E9ED", lw=.5)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(loc="upper left", bbox_to_anchor=(.01, 1.08), frameon=False, fontsize=6.7)
    ax.tick_params(axis="both", length=2.5, labelsize=7.2)
    save(fig, "cobertura_sintetica")


scheme()
effects()
coverage()
print("Version matplotlib:", matplotlib.__version__)
