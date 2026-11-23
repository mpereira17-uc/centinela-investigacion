# Registro de cambios de alcance

## Versión 1.1.0 | 17 de noviembre de 2026

- Se centra el artículo en el diseño del mecanismo de alertas del aplicativo y su integración prevista con transcripción y clasificador. El aporte de software es una especificación ejecutable de la decisión de alerta.
- Se añade motor_alertas.py, ocho comprobaciones lógicas y auditar_motor.py. No se construyó ni se probó el aplicativo con audio.
- Se mantienen sin cambios el generador, sus parámetros, semillas, CSV y métricas del primer análisis. Las 320 trazas no son 320 audios y no se usan como corpus entrenado.
- Se comprueba el acuerdo de primeros avisos al ejecutar el motor contra la referencia. La primera alerta es inmutable; reenvíos y revisiones tardías se registran sin duplicarla.
- El contrato, las colas del adaptador y la presentación del aviso se describen como diseño. La cadencia inicial de dos segundos se debe comprobar con audio. El umbral 1,15 es solo el del generador.
- El corpus reservado, la selección del transcriptor y los parámetros del clasificador se fijarán antes del ensayo con audio. El depósito DOI, la revisión cruzada y la devolución siguen pendientes.

## Versión 1.0.0 | 16 de noviembre de 2026

Se ejecutó la prueba del análisis con puntuaciones sintéticas (Ruta B), sin audio, entrenamiento ni usuarios. Tras la primera ejecución se añadió el intervalo de la mediana pareada como comprobación secundaria; no se cambiaron datos ni contrastes principales. El plazo de seis segundos tiene seguimiento incompleto en 50 llamadas de riesgo. No se excluyeron trazas.
