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

## Generador y trazas

El generador de las 320 trazas (semillas 20261116 y 20261117), el motor de referencia y sus pruebas forman el paquete del artículo. Aún no tiene DOI; se puede pedir a mpereira17@ucatolica.edu.co.

## Licencias

Código: MIT. Datos sintéticos: CC0. Artículo, póster y figuras: CC BY 4.0.
