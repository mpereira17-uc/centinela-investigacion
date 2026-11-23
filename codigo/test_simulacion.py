"""Comprobaciones del cálculo y de la integridad del banco sintético."""
import json
import math
import unittest
from collections import Counter
from pathlib import Path

from simular import CONFIG, context_score, evaluate, first_alert, generate, proportions, quantile, status

ROOT = Path(__file__).resolve().parents[1]


class Verificacion(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = json.loads(CONFIG.read_text(encoding="utf-8"))
        cls.calls, cls.fragments = generate(cls.config)
        cls.rows = evaluate(cls.calls, cls.config, cls.config["umbral_comun"], cls.config["plazo_principal_s"])
        cls.reported = json.loads((ROOT / "resultados/metricas_sinteticas.json").read_text(encoding="utf-8"))

    def test_intervalos_operativos(self):
        answers = [status(t, 10, 4) for t in [None, 9.9, 10, 14, 14.1]]
        self.assertEqual(answers, ["omitida", "anticipada", "oportuna", "oportuna", "tardia"])
        self.assertEqual(status(0, None, 4), "falsa_alerta")

    def test_primera_alerta_no_usa_futuro(self):
        fragments = [
            dict(score=0.0, fin_fragmento_s=2, latencia_simulada_s=.5),
            dict(score=2.0, fin_fragmento_s=4, latencia_simulada_s=.5),
            dict(score=3.0, fin_fragmento_s=6, latencia_simulada_s=.5),
        ]
        for strategy in ("F", "C"):
            self.assertEqual(first_alert(fragments, "score", strategy, 1, [1, .7, .5]), 4.5)
            self.assertIsNone(first_alert(fragments[:1], "score", strategy, 1, [1, .7, .5]))

    def test_contexto_respeta_historial_maximo(self):
        weights = [1, .7, .5]
        self.assertAlmostEqual(context_score([5, 1, 0, 2], weights), 2.5 / math.sqrt(1.74))
        self.assertEqual(context_score([2], weights), 2)

    def test_grupos_balanceados_y_tiempos(self):
        counters = Counter((c["familia"], c["etiqueta"], c["condicion"]) for c in self.calls)
        self.assertEqual(len(counters), 64)
        self.assertEqual(set(counters.values()), {5})
        self.assertEqual(len(self.calls), len({c["id_llamada"] for c in self.calls}))
        self.assertEqual(len(self.fragments), 2560)
        for r in self.rows:
            if r["etiqueta"]:
                self.assertGreater(r["horizonte_s"], r["t0_s"] + 4)
            for s in ("F", "C"):
                first = r[f"alerta_{s}_perturbada_s"]
                if first is not None:
                    self.assertLessEqual(first, r["horizonte_s"])

    def test_conteos_y_denominadores(self):
        for s in ("F", "C"):
            p = proportions(self.rows, s)
            self.assertEqual(p["anticipadas"] + p["oportunas"] + p["tardias"] + p["omitidas"], 160)
            self.assertAlmostEqual(p["falsas"] / 160, p["falsas_alertas"])
            self.assertAlmostEqual(p["detectadas"] / 160, p["sensibilidad"])
            for name in p:
                self.assertEqual(p[name], self.reported["principales"][s][name])

    def test_wer_micro_y_fechas_de_simulacion(self):
        n = sum(f["ref_palabras"] for f in self.fragments)
        e = 0
        for f in self.fragments:
            self.assertEqual(f["tipo_dato"], "sintetico")
            self.assertLessEqual(f["sustituciones_sim"] + f["omisiones_sim"], f["ref_palabras"])
            e += f["sustituciones_sim"] + f["omisiones_sim"] + f["inserciones_sim"]
        self.assertAlmostEqual(e / n, self.reported["wer_simulado"])

    def test_percentiles_y_reproducibilidad(self):
        self.assertAlmostEqual(quantile([0, 1, 2, 3, 4], .95), 3.8)
        self.assertIsNone(quantile([], .5))
        generated = generate(self.config)
        self.assertEqual(generated, (self.calls, self.fragments))


if __name__ == "__main__":
    unittest.main(verbosity=2)
