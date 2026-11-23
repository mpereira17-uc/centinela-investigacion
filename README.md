# Centinela · Investigación (tercer corte, ruta B)

Material del póster y del artículo *Centinela: diseño del mecanismo de alertas para llamadas simuladas*.
Mathew Pereira Uribe · Director: Carlos Mauricio Blanco Muñoz · Ingeniería de Sistemas y Computación, Universidad Católica de Colombia.

> **Ruta B: protocolo con prueba de análisis simulada.** Todas las cifras salen de 320 llamadas **simuladas**. No son llamadas reales ni miden el desempeño del aplicativo.

| Carpeta | Contenido |
|---|---|
| `articulo/` | Artículo en PDF |
| `poster/` | Póster en PDF (A0) |
| `figuras/` | `figuras.py`, `datos_tabla_ii.csv` (Tabla II del artículo) y las dos figuras en SVG y PNG |

## Repetir las figuras

```
pip install matplotlib
cd figuras
python figuras.py
```

## Generador, motor y datos (paquete del artículo)

| Carpeta | Contenido |
|---|---|
| `codigo/` | `simular.py` (genera las 320 trazas), `motor_alertas.py`, `auditar_motor.py`, `graficar.py` y 15 pruebas |
| `protocolo/` | `configuracion.json` (parámetros y semillas 20261116 y 20261117), protocolo y registro de cambios |
| `datos/` | 320 llamadas y 2560 fragmentos sintéticos, con diccionario de variables |
| `resultados/` | métricas, intervalos, sensibilidad por umbral y plazo, auditoría del motor y huellas SHA-256 |
| `documento/` | fuente editable del artículo y sus figuras |

Detalle del paquete en [PAQUETE.md](PAQUETE.md).

```
python codigo/test_simulacion.py
python codigo/auditar_motor.py
python codigo/simular.py --salida prueba_nueva
```

Comprobado el 23 de noviembre de 2026: los CSV y las métricas se reproducen idénticos (solo cambia la versión de Python anotada) y pasan las 15 pruebas.

## Licencias

Código: MIT (`LICENSE-CODE.txt`). Datos sintéticos: CC0 (`LICENSE-DATA.txt`). Póster y figuras: CC BY 4.0. Cita: `CITATION.cff`.
