# Centinela | Mecanismo de alertas del aplicativo

**Versión del paquete:** 1.1.0, 17 de noviembre de 2026.  
**Autor del anteproyecto y contacto:** Mathew Pereira Uribe, Universidad Católica de Colombia, mpereira17@ucatolica.edu.co.  
**Ruta B:** protocolo con prueba de análisis simulada. El artículo profundiza en el diseño e integración del mecanismo de alertas.

El motor de referencia recibe puntuaciones numéricas, aplica las reglas F y C y conserva cada primer aviso. No incluye Whisper, un clasificador entrenado, una interfaz de usuario ni captura de llamadas. Las decisiones auditadas provienen de 320 trazas sintéticas: no son conversaciones ni casos de fraude observados. Las etiquetas «llamada» y «familia» son unidades del banco generado.

## Ejecutar la comprobación

Use Python 3.12.14 desde la carpeta descomprimida. Generación, pruebas y motor solo usan biblioteca estándar.

```sh
python codigo/test_simulacion.py
python codigo/auditar_motor.py
```

El primer comando verifica los cálculos del generador. El segundo ejecuta las ocho pruebas lógicas del motor, reproduce las entradas de referencia y perturbadas, y escribe resultados/verificacion_motor.json. Para esta entrega obtuvo 1280 comparaciones sin divergencias y 10240 decisiones registradas. Coincidir con la referencia no evalúa la transcripción ni garantiza que un modelo reconozca estafas.

Para volver a generar las trazas originales de la versión 1.0.0:

```sh
python codigo/simular.py
```

Use --salida con una carpeta distinta si quiere preservar las salidas originales. El generador emplea las semillas 20261116 (datos) y 20261117 (remuestreo por familia). Su configuración está en protocolo/configuracion.json. Los CSV y las métricas conservan su versión de generación 1.0.0; no se cambiaron para favorecer una regla.

Las figuras nuevas y la fuente del artículo están en documento/. El Word editable acompaña la entrega y se incluye en ese directorio. El script codigo/graficar.py regenera las figuras de la simulación de la versión 1.0.0, con Matplotlib 3.10.8. El Word usa el gráfico de diferencias y un esquema de integración adicional. Todos los archivos del paquete se identifican en MANIFEST_SHA256.txt.

## Archivos principales

- codigo/motor_alertas.py: recepción ordenada, separación por llamada, decisiones F/C, primera alerta y eventos de error.
- codigo/test_motor.py: ocho pruebas de comportamiento, incluidos duplicados y revisiones tardías.
- codigo/auditar_motor.py: comparación del motor contra los tiempos de los CSV originales.
- datos/: trazas sintéticas por llamada y fragmento, con su diccionario.
- resultados/: métricas e intervalos de la simulación y nueva auditoría del motor.
- protocolo/: modelo generador, protocolo fechado y registro de cambios de alcance.
- documento/: manuscrito editable y figuras del artículo adaptado.

## Acceso y licencias

No existe un DOI público de esta versión. El paquete se adjunta a la entrega académica y puede solicitarse al correo de correspondencia. Los datos sintéticos no tienen una restricción por privacidad. El autor debe gestionar el depósito con DOI, la validación de autoría y la comprobación de acceso sin cuenta; no se afirma que ese requisito esté resuelto.

El código propio del banco y del motor se suministra bajo MIT (LICENSE-CODE.txt); los datos sintéticos y sus salidas numéricas, bajo CC0 1.0 (LICENSE-DATA.txt). La fuente del artículo no queda cubierta por CC0. No se incluyen bibliotecas ni modelos de terceros. El artículo declara el apoyo de IA en código y redacción.

Cita sugerida: M. Pereira Uribe, «Centinela: mecanismo de alertas y paquete de comprobación sintética», versión 1.1.0, Universidad Católica de Colombia, 2026, material adjunto al artículo.
