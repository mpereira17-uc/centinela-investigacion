#!/usr/bin/env python3
"""Genera y evalúa trazas sintéticas para Centinela. Solo biblioteca estándar."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import random
import statistics
import sys
from collections import Counter
from pathlib import Path

VERSION = "1.0.0"
ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "protocolo/configuracion.json"


def quantile(values, q):
    """Percentil con interpolación lineal (Hyndman y Fan, tipo 7)."""
    if not values:
        return None
    v = sorted(values)
    k = (len(v) - 1) * q
    a = math.floor(k)
    return v[a] + (v[math.ceil(k)] - v[a]) * (k - a)


def context_score(values, weights):
    recent = list(reversed(values[-len(weights):]))
    local_weights = weights[:len(recent)]
    return sum(w * s for w, s in zip(local_weights, recent)) / math.sqrt(
        sum(w * w for w in local_weights)
    )


def generate(config):
    rng = random.Random(config["semilla_datos"])
    calls, fragments = [], []
    k_max, cadence = config["fragmentos"], config["segundos_por_fragmento"]
    for fam in range(1, config["familias"] + 1):
        group = f"F{fam:02d}"
        family_effect = rng.gauss(0, config["desviacion_familia"])
        for label in (0, 1):
            for condition in config["condiciones"]:
                errors = config["errores_por_condicion"][condition]
                for _ in range(config["llamadas_por_clase_y_condicion_en_familia"]):
                    ident = f"S{len(calls) + 1:04d}"
                    event = rng.choice(config["indice_inicio_riesgo"]) if label else None
                    call_effect = rng.gauss(0, config["desviacion_llamada"])
                    if label:
                        profiles = config["perfiles_riesgo"]
                        profile = rng.choices(list(profiles), [p["probabilidad"] for p in profiles.values()])[0]
                    else:
                        profile = "ambigua" if rng.random() < config["legitimas"]["probabilidad_ambigua"] else "clara"
                    spike_at = rng.randint(2, k_max - 1) if profile == "ambigua" else None
                    spike_amp = rng.uniform(*config["legitimas"]["pico_intervalo"]) if spike_at else 0
                    call = dict(
                        id_llamada=ident, familia=group, etiqueta=label, condicion=condition,
                        perfil=profile, t0_s=event * cadence if event else None,
                        tipo_dato="sintetico", fragmentos=[],
                    )
                    for k in range(1, k_max + 1):
                        if label:
                            shift = profiles[profile]["incrementos"].get(str(k - event), 0.0)
                        else:
                            shift = (
                                spike_amp if k == spike_at else
                                spike_amp * config["legitimas"]["proporcion_pico_siguiente"]
                                if spike_at is not None and k == spike_at + 1 else 0.0
                            )
                        score = (config["base_puntuacion"] + family_effect + call_effect +
                                 shift + rng.gauss(0, config["desviacion_fragmento"]))
                        n_words = rng.randint(*config["palabras_fragmento"])
                        subs = dels = ins = 0
                        for _word in range(n_words):
                            draw = rng.random()
                            if draw < errors["sustitucion"]:
                                subs += 1
                            elif draw < errors["sustitucion"] + errors["omision"]:
                                dels += 1
                            ins += int(rng.random() < errors["insercion"])
                        wer = (subs + dels + ins) / n_words
                        p = config["perturbacion"]
                        ref = round(score, 10)
                        asr = round(ref - p["coeficiente_wer"] * wer + rng.gauss(
                            0, p["desviacion_base"] + p["desviacion_por_unidad_wer"] * wer
                        ), 10)
                        lag = round(config["latencia_base_s"] + errors["latencia_extra_s"] +
                                    rng.uniform(0, config["latencia_uniforme_max_s"]), 10)
                        f = dict(
                            id_llamada=ident, indice=k, fin_fragmento_s=k * cadence,
                            latencia_simulada_s=lag, ref_palabras=n_words,
                            sustituciones_sim=subs, omisiones_sim=dels, inserciones_sim=ins,
                            evidencia_ref_sim=ref, evidencia_perturbada_sim=asr, tipo_dato="sintetico",
                        )
                        fragments.append(f)
                        call["fragmentos"].append(f)
                    calls.append(call)
    return calls, fragments


def first_alert(fragments, campo, strategy, threshold, weights):
    history = []
    for piece in fragments:
        history.append(piece[campo])
        score = history[-1] if strategy == "F" else context_score(history, weights)
        if score >= threshold:
            return round(piece["fin_fragmento_s"] + piece["latencia_simulada_s"], 10)
    return None


def status(t, t0, deadline):
    if t is None:
        return "omitida" if t0 is not None else "sin_alerta"
    if t0 is None:
        return "falsa_alerta"
    dt = t - t0
    if dt < 0:
        return "anticipada"
    return "oportuna" if dt <= deadline else "tardia"


def evaluate(calls, config, threshold, deadline):
    weights = config["pesos_contexto"]
    results = []
    for call in calls:
        fs = call["fragmentos"]
        out = {k: v for k, v in call.items() if k != "fragmentos"}
        out["horizonte_s"] = round(fs[-1]["fin_fragmento_s"] + fs[-1]["latencia_simulada_s"], 10)
        out["palabras_ref"] = sum(f["ref_palabras"] for f in fs)
        out["errores_sim"] = sum(f["sustituciones_sim"] + f["omisiones_sim"] + f["inserciones_sim"] for f in fs)
        for strategy in ("F", "C"):
            ref = first_alert(fs, "evidencia_ref_sim", strategy, threshold, weights)
            t = first_alert(fs, "evidencia_perturbada_sim", strategy, threshold, weights)
            out[f"alerta_{strategy}_ref_s"] = ref
            out[f"alerta_{strategy}_perturbada_s"] = t
            out[f"demora_{strategy}_s"] = round(t - call["t0_s"], 10) if t is not None and call["etiqueta"] else None
            out[f"estado_{strategy}"] = status(t, call["t0_s"], deadline)
            out[f"cambio_{strategy}"] = int((ref is None) != (t is None))
        results.append(out)
    return results


def proportions(rows, strategy):
    positives = [r for r in rows if r["etiqueta"] == 1]
    negatives = [r for r in rows if r["etiqueta"] == 0]
    counts = Counter(r[f"estado_{strategy}"] for r in rows)
    pos, neg = len(positives), len(negatives)
    tp = pos - counts["omitida"]
    fp = counts["falsa_alerta"]
    return {
        "n_riesgo": pos, "n_legitimas": neg, "detectadas": tp,
        "anticipadas": counts["anticipada"], "oportunas": counts["oportuna"],
        "tardias": counts["tardia"], "omitidas": counts["omitida"], "falsas": fp,
        "sensibilidad": tp / pos if pos else None,
        "oportunidad": counts["oportuna"] / pos if pos else None,
        "falsas_alertas": fp / neg if neg else None,
        "precision": tp / (tp + fp) if tp + fp else None,
        "f1": 2 * tp / (tp + fp + pos) if tp + fp + pos else None,
    }


def bootstrap(rows, config):
    """Conserva pares y conglomerados: cada unidad extraída es una familia."""
    groups = {}
    for r in rows:
        groups.setdefault(r["familia"], []).append(r)
    keys = sorted(groups)
    metrics = ("sensibilidad", "oportunidad", "falsas_alertas")
    stats = {m: {"F": [], "C": [], "C_menos_F": []} for m in metrics}
    medians = []
    rng = random.Random(config["semilla_bootstrap"])
    for _ in range(config["n_bootstrap"]):
        selected = [rng.choice(keys) for _ in keys]
        base = [r for fam in selected for r in groups[fam]]
        f, c = (proportions(base, s) for s in ("F", "C"))
        for m in metrics:
            stats[m]["F"].append(f[m])
            stats[m]["C"].append(c[m])
            stats[m]["C_menos_F"].append(c[m] - f[m])
        pairs = [
            r["demora_C_s"] - r["demora_F_s"] for r in base
            if r["demora_F_s"] is not None and r["demora_C_s"] is not None
        ]
        if pairs:
            medians.append(quantile(pairs, .5))
    intervals = {
        m: {s: [quantile(v, .025), quantile(v, .975)] for s, v in variants.items()}
        for m, variants in stats.items()
    }
    intervals["demora_pareada_s"] = {
        "C_menos_F": [quantile(medians, .025), quantile(medians, .975)],
        "replicas_validas": len(medians),
    }
    return intervals


def describe(rows, strategy):
    out = proportions(rows, strategy)
    delays = [r[f"demora_{strategy}_s"] for r in rows if r[f"demora_{strategy}_s"] is not None]
    out.update(
        mediana_s=quantile(delays, .5), p95_s=quantile(delays, .95),
        n_demora=len(delays), cambios_ref_perturbada=sum(r[f"cambio_{strategy}"] for r in rows),
        alertas_ref=sum(r[f"alerta_{strategy}_ref_s"] is not None for r in rows),
    )
    return out


def analyze(rows, calls, config):
    paired = [r["demora_C_s"] - r["demora_F_s"] for r in rows
              if r["demora_F_s"] is not None and r["demora_C_s"] is not None]
    incidence = {"F_solo": 0, "C_solo": 0, "ambas": 0, "ninguna": 0}
    for r in (r for r in rows if r["etiqueta"]):
        f, c = (r[f"demora_{s}_s"] is not None for s in ("F", "C"))
        incidence["ambas" if f and c else "F_solo" if f else "C_solo" if c else "ninguna"] += 1
    out = {
        "version": VERSION, "tipo_dato": "sintetico", "python": sys.version.split()[0],
        "n": len(rows), "familias": len({r["familia"] for r in rows}),
        "principales": {s: describe(rows, s) for s in ("F", "C")},
        "ic95_bootstrap": bootstrap(rows, config),
        "wer_simulado": sum(r["errores_sim"] for r in rows) / sum(r["palabras_ref"] for r in rows),
        "palabras_ref_total": sum(r["palabras_ref"] for r in rows),
        "errores_sim_total": sum(r["errores_sim"] for r in rows),
        "incidencia_deteccion_pareada_riesgo": incidence,
        "demora_pareada": {"n": len(paired), "mediana_C_menos_F_s": quantile(paired, .5)},
        "condiciones": {}, "familia": [], "sensibilidad_analitica": []
    }
    for cond in config["condiciones"]:
        subset = [r for r in rows if r["condicion"] == cond]
        out["condiciones"][cond] = dict(
            n=len(subset),
            wer=sum(r["errores_sim"] for r in subset) / sum(r["palabras_ref"] for r in subset),
            **{s: describe(subset, s) for s in ("F", "C")},
        )
    for fam in sorted({r["familia"] for r in rows}):
        subset = [r for r in rows if r["familia"] == fam]
        out["familia"].append(dict(familia=fam, n=len(subset),
                                   **{s: describe(subset, s) for s in ("F", "C")}))
    for threshold in config["umbrales_sensibilidad"]:
        for delay in config["plazos_sensibilidad_s"]:
            trial = evaluate(calls, config, threshold, delay)
            for s in ("F", "C"):
                p = proportions(trial, s)
                out["sensibilidad_analitica"].append({
                    "tipo_dato": "sintetico", "umbral": threshold, "plazo_s": delay, "estrategia": s,
                    "n_riesgo": p["n_riesgo"], "n_legitimas": p["n_legitimas"],
                    "oportunas": p["oportunas"], "oportunidad": p["oportunidad"],
                    "falsas": p["falsas"], "falsas_alertas": p["falsas_alertas"],
                    "n_riesgo_observacion_incompleta": sum(
                        1 for r in trial if r["etiqueta"] and r["t0_s"] + delay > r["horizonte_s"]
                    ),
                })
    return out


def write_csv(path, rows):
    with path.open("w", encoding="utf-8", newline="") as out:
        w = csv.DictWriter(out, fieldnames=list(rows[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=CONFIG)
    parser.add_argument("--salida", type=Path, default=ROOT)
    args = parser.parse_args()
    config = json.loads(args.config.read_text(encoding="utf-8"))
    calls, fragments = generate(config)
    rows = evaluate(calls, config, config["umbral_comun"], config["plazo_principal_s"])
    metrics = analyze(rows, calls, config)
    data, results = (args.salida / sub for sub in ("datos", "resultados"))
    for d in (data, results):
        d.mkdir(parents=True, exist_ok=True)
    write_csv(data / "fragmentos_sinteticos.csv", fragments)
    write_csv(data / "llamadas_sinteticas.csv", rows)
    write_csv(results / "sensibilidad_umbral_plazo.csv", metrics["sensibilidad_analitica"])
    (results / "metricas_sinteticas.json").write_text(
        json.dumps(metrics, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    names = sorted([*data.glob("*.csv"), *results.glob("*.csv"), results / "metricas_sinteticas.json"])
    with (results / "huellas_sha256.txt").open("w", encoding="utf-8") as target:
        for path in names:
            print(hashlib.sha256(path.read_bytes()).hexdigest(), path.relative_to(args.salida).as_posix(), file=target, sep="  ")
    print(f"Solo simulación: {len(rows)} llamadas, {len(fragments)} fragmentos, {metrics['familias']} familias.")


if __name__ == "__main__":
    main()
