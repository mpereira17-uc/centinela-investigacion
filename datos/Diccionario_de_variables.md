# Diccionario de variables | Centinela

Datos **sintéticos**, versión 1.0.0. CSV separados por coma, UTF-8, punto decimal. Un valor vacío significa que el campo no aplica o que no hubo alerta; no se imputa como cero. Todos los segundos se miden desde el inicio de la llamada sintética. La clave que vincula los CSV es id_llamada.

## llamadas_sinteticas.csv (320 filas; una por llamada)

| Variable | Tipo o unidad | Interpretación |
| --- | --- | --- |
| id_llamada | Texto, S0001–S0320 | Identificador único sin vínculo con personas. |
| familia | Texto, F01–F16 | Conglomerado de 20 llamadas con un desplazamiento compartido. |
| etiqueta | Entero 0/1 | 0 legítima; 1 riesgo, fijada por el generador. |
| condicion | Categoría | baja_perturbacion o alta_perturbacion; no corresponde a grabaciones. |
| perfil | Categoría | clara/ambigua para legítimas; dispersa/concentrada/debil para riesgo. |
| t0_s | Segundos o vacío | Fin sintético de la primera petición de riesgo: 8, 10 o 12 s. |
| tipo_dato | Texto | Siempre sintetico. |
| horizonte_s | Segundos | Instante de decisión del último fragmento, incluida latencia simulada. |
| palabras_ref | Conteo | Palabras de referencia simuladas, sumadas en la llamada. |
| errores_sim | Conteo | Suma de sustituciones, omisiones e inserciones simuladas. |
| alerta_F_ref_s, alerta_C_ref_s | Segundos o vacío | Instante de primer aviso con evidencia de referencia, por estrategia. |
| alerta_F_perturbada_s, alerta_C_perturbada_s | Segundos o vacío | Instante de primer aviso con evidencia perturbada. |
| demora_F_s, demora_C_s | Segundos o vacío | Alerta perturbada menos t0_s, solo en riesgo detectado. Puede ser negativa. |
| estado_F, estado_C | Categoría | anticipada, oportuna, tardia, omitida, falsa_alerta o sin_alerta. |
| cambio_F, cambio_C | Entero 0/1 | 1 si cambia la presencia de alerta entre referencia y perturbada. No mide cambios solo de tiempo. |

F = regla por fragmento. C = regla con contexto. Oportuna incluye los extremos de 0 a 4 s en el análisis principal. Una legítima con aviso es falsa_alerta.

## fragmentos_sinteticos.csv (2560 filas; ocho por llamada)

| Variable | Tipo o unidad | Interpretación |
| --- | --- | --- |
| id_llamada | Texto | Identificador de la llamada sintética. |
| indice | Entero, 1–8 | Orden del fragmento. |
| fin_fragmento_s | Segundos | 2, 4, ..., 16 s. |
| latencia_simulada_s | Segundos | Retardo generado tras el cierre; compartido por F y C. |
| ref_palabras | Conteo, 8–20 | Número generado de palabras de referencia. |
| sustituciones_sim, omisiones_sim, inserciones_sim | Conteo | Errores generados para probar la fórmula de WER. |
| evidencia_ref_sim | Real | Puntaje de referencia sin perturbación; no es probabilidad. |
| evidencia_perturbada_sim | Real | Puntaje posterior a la perturbación; no es probabilidad. |
| tipo_dato | Texto | Siempre sintetico. |

## Salidas del análisis

metricas_sinteticas.json contiene conteos, proporciones en escala 0–1, tiempos en segundos, intervalos de remuestreo, métricas por condición y por familia. C_menos_F se almacena como diferencia de proporciones, sin multiplicar por 100; el artículo la expresa en puntos porcentuales. El CSV sensibilidad_umbral_plazo.csv indica estrategia, umbral, plazo, denominadores, proporciones y número de llamadas de riesgo con horizonte insuficiente. No se extrapola su seguimiento. El WER agregado divide errores totales por palabras totales; no promedia cocientes de fragmentos.
