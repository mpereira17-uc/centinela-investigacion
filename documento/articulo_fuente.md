# Centinela Diseño del mecanismo de alertas para llamadas simuladas
@autor Mathew Pereira Uribe
@afiliacion Ingeniería de Sistemas y Computación, Universidad Católica de Colombia
@ciudad Bogotá D. C., Colombia
@correo mpereira17@ucatolica.edu.co
@ruta Tercer corte | Ruta B Protocolo con prueba de análisis simulada

@resumen Una advertencia de posible fraude necesita llegar mientras la persona aún puede verificar la petición. En Centinela, el problema de diseño es decidir qué información de la conversación conservar y cómo convertirla en un aviso que pueda rastrearse después. Este artículo desarrolla el diseño del mecanismo de alertas de un aplicativo para llamadas simuladas en español. Se especifican el recorrido del audio, el intercambio de datos entre componentes y dos reglas: una decide por fragmento y la otra combina las tres puntuaciones más recientes. Se implementó un motor de referencia que recibe puntuaciones, registra ambas decisiones y evita repetir la primera alerta. Su comportamiento se comprobó con ocho pruebas lógicas y con la reproducción de 320 trazas numéricas sintéticas. Las 1280 comparaciones de primeros avisos coincidieron con los cálculos del generador. En el escenario sintético, incorporar contexto redujo las falsas alertas de 24 a 8 entre 160 llamadas legítimas, pero también los avisos oportunos de 75 a 59 entre 160 llamadas de riesgo. La comprobación respalda la consistencia del motor bajo esas entradas, sin evaluar aún la transcripción ni el aplicativo con audio. El aporte es una especificación ejecutable de la decisión de alerta y un plan para comprobar su integración antes de elegir una estrategia.
@claves Ingeniería de software, alertas conversacionales, fraude telefónico, integración de modelos, simulación.

## I. INTRODUCCIÓN
### A. Una decisión durante la llamada
Una petición de un código o un pago puede parecer parte de un trámite conocido. Quien recibe la llamada debe decidir si la atiende, si verifica la identidad del interlocutor o si termina la conversación. El Centro Cibernético Policial describe el vishing financiero como una suplantación por voz para obtener información personal o financiera [1]. Esa descripción institucional orienta los guiones de Centinela. Las personas que podrían recibir esas solicitudes son sus destinatarias potenciales; en este corte no se consultó a víctimas.

En el corte de marzo de 2026, el Ministerio de Defensa registró 13.417 hechos de extorsión en 2025 y 2.914 entre enero y marzo de 2026, con cifras sujetas a revisión [2]. Los datos reúnen distintas modalidades. Sirven para ubicar el problema, pero no permiten aislar las llamadas fraudulentas ni estimar cuántas evitaría una aplicación. El trabajo se concentra en una decisión de software: cuándo mostrar un aviso a partir de lo que se ha dicho hasta ese momento.

### B. Antecedentes y aporte específico
MOAN, desarrollada en Colombia, consultaba si el número entrante tenía reportes para orientar la actuación ante una posible extorsión [3]. CallKnight planteó identificar llamadas fraudulentas mientras ocurrían, aunque la noticia institucional no documenta una comparación entre fragmentos y contexto [4]. Google también describe alertas durante ciertas llamadas [5]. El análisis conversacional tiene antecedentes y, por sí solo, no es la contribución que se atribuye a Centinela.

Shen et al. señalaron sesgos en los datos y limitaciones de la detección de estafas telefónicas [6]; en otro trabajo estudiaron el momento de la advertencia [7]. Lu y Chen compararon decisiones por segmentos y votación semántica con diálogos sintéticos en mandarín [8]. Estos trabajos motivan la pregunta por el contexto, pero sus cifras no se trasladan a los escenarios del proyecto. También importa la forma de integrar el detector: una advertencia repetida, un texto corregido después o un fragmento fuera de orden pueden alterar el registro, incluso con el mismo puntaje de riesgo.

### C. Foco del artículo
El proyecto de grado busca desarrollar un aplicativo que transcriba y analice llamadas simuladas en español para advertir solicitudes con indicios de fraude. Aquí se profundiza en su mecanismo de alertas: el contrato entre transcripción, puntuación y aviso, las dos reglas de decisión y la evidencia que permitirá revisar sus errores. Whisper y el clasificador son componentes de la solución. No se propone entrenar desde cero un nuevo modelo de reconocimiento de voz.

La pregunta del artículo es cómo integrar decisiones por fragmento y por contexto en un mismo recorrido de procesamiento, conservando la primera alerta y permitiendo una comparación por llamada. El objetivo de este corte es especificar ese mecanismo y comprobar su lógica con puntuaciones sintéticas. El aporte es el motor de referencia, su registro verificable y el protocolo que separa la corrección del software del futuro desempeño con audio.

## II. METODOLOGÍA
### A. Enfoque y alcance de la comprobación
Se sigue un enfoque de desarrollo tecnológico con comparación cuantitativa y pareada. La postura es postpositivista: las etiquetas y los plazos se definen para medir, pero pueden discutirse si los supuestos no se sostienen. La llamada completa será la unidad de análisis. Probar ambas reglas con la misma secuencia permite estudiar el uso del contexto sin confundirlo con diferencias del guion o del audio.

Se conserva la Ruta B. En este corte se documentó el diseño, se implementó el motor de referencia y se ejecutó la prueba numérica. Los adaptadores de audio, el clasificador entrenado y la interfaz están previstos; no se presentan como construidos. El motor permite ejecutar la lógica de alerta sin depender todavía de esos componentes. Una prueba satisfactoria del motor no certifica que una transcripción sea correcta.

### B. Recorrido del audio hasta el puntaje
La entrada prevista será una llamada guionada cuyo audio controle el aplicativo, o una reproducción que respete el tiempo de sus fragmentos. Se inicia con una cadencia propuesta de dos segundos, consistente con la prueba sintética. Esa cadencia es una decisión inicial que deberá verificarse en la prueba preliminar. Si la transcripción tarda más de lo que dura el fragmento, se documentará la acumulación de trabajo y no se anunciará funcionamiento en tiempo real.

Whisper convertirá el audio en texto [9]. El adaptador deberá manejar la revisión de palabras al recibir más audio, dificultad abordada por Macháček et al. en su adaptación a transcripción continua [10]. El motor solo recibirá fragmentos confirmados. Antes de confirmar podrán corregirse; después, una revisión quedará en la auditoría sin reescribir la decisión que ya habría visto el usuario. Se propone así una primera versión reproducible, cuya pérdida de información por correcciones tardías deberá medirse aparte.

Con el texto confirmado se obtendrá una representación TF-IDF [11] y una regresión logística producirá un puntaje de evidencia [12]. El diseño prevé unigramas y bigramas, conservando las negaciones. Se usará la función de decisión del clasificador, de modo que el motor reciba un valor numérico y no dependa de la librería que lo calculó. El vocabulario y los parámetros se ajustarán solo con entrenamiento. No se ejecutó ese entrenamiento en la comprobación de este artículo.

Las dos reglas recibirán el mismo puntaje por fragmento. Así se cambia la forma de incorporar evidencia anterior, sin ejecutar dos transcriptores o dos clasificadores distintos. El umbral será común, elegido en validación y congelado antes de la reserva. Compartir umbral no garantiza la misma tasa de falsas alertas: al combinar puntajes cambia su distribución. Esa diferencia deberá informarse y revisarse con los umbrales alternativos.

@figura arquitectura
Figura 1. Arquitectura propuesta del mecanismo de alertas. El bloque de referencia se ejecutó con puntajes sintéticos; audio, transcripción, clasificador e interfaz siguen pendientes de integración.

### C. Contrato y orden de los fragmentos
La Tabla I resume la entrada del motor. Una instancia pertenece a una sola llamada y usa su propio historial, con un máximo de tres puntajes. Un fragmento debe llegar después del anterior. Si falta uno o llega fuera de secuencia, se rechaza esa entrada y se registra la incidencia, sin inventar un puntaje para cubrir el vacío. El adaptador tendrá que recuperar el orden antes de continuar o declarar el análisis no disponible.

La combinación de llamada, número y revisión identifica cada entrada confirmada. Reenviar exactamente la misma entrada no produce otra decisión ni otro aviso. Si cambia el contenido bajo el mismo identificador confirmado se registra un conflicto. Una revisión posterior no altera el puntaje ya usado ni el primer aviso. Esta regla evita que una corrección tardía haga parecer que el sistema había alertado antes.

@tabla contrato
Tabla I. Entrada mínima del motor de referencia.

La disponibilidad debe ser posterior al cierre del fragmento y no retroceder respecto a entradas anteriores. En el ensayo con audio se usarán marcas de un mismo reloj monotónico por sesión. El tiempo del archivo sirve para ubicar la petición; el reloj de procesamiento permite reconstruir cuándo se pudo mostrar el aviso. El registro conservará ambos y su correspondencia.

### D. Reglas y comportamiento del aviso
Sea z(i,k) el puntaje confirmado del fragmento k en la llamada i. F compara el puntaje actual con el umbral. C combina el actual y hasta dos anteriores, con pesos 1,00, 0,70 y 0,50, respectivamente:
@ecuacion reglas
Ecuación 1. Reglas del motor con q = min(2, k − 1) y pesos w = (1; 0,70; 0,50).

Al iniciar una llamada se usan los pesos del historial disponible. La normalización compensa la suma de residuos independientes, pero no elimina la correlación ni transforma el resultado en probabilidad. El historial acotado evita que una intervención antigua pese durante toda la conversación. Es una elección de diseño que se contrastará con validación, no una propiedad óptima ya demostrada.

Como ejemplo artificial, una secuencia de puntajes 0,30; 0,90; 0,90; 1,40 hace que C cruce 1,15 en el tercer fragmento, mientras F lo cruza en el cuarto. También puede ocurrir lo contrario: un pico breve puede diluirse entre valores previos bajos. La simulación incluye esos perfiles para examinar ambos comportamientos. El valor 1,15 se fijó para el generador; no se asumirá como umbral del futuro clasificador.

Cada fragmento válido produce dos registros de decisión. La primera vez que una regla cruza el umbral se conserva su instante; las siguientes decisiones continúan en la auditoría, sin crear otro primer aviso. En la interfaz prevista se elegirá qué regla mostrar durante la demostración, aunque se registren ambas. El mensaje advertirá de una posible solicitud de riesgo y sugerirá verificarla. No dirá que el interlocutor cometió un delito.

Si falla un componente, el estado visible deberá ser «Análisis no disponible». Ausencia de alerta y fallo de análisis son estados distintos. El motor de referencia impide seguir clasificando una sesión marcada como fallida o cerrada. El control de espera de la interfaz y el tratamiento de la cola de audio se probarán durante la integración; no forman parte de las mediciones sintéticas.

### E. Auditoría y pruebas de integración previstas
Por fragmento se conservan el identificador de llamada, la secuencia, la revisión confirmada, el puntaje, el umbral, los tiempos y la versión del motor. Cada decisión indica la regla utilizada y si produjo su primera alerta. Las versiones de transcripción y del clasificador se asociarán a la sesión al integrar esos componentes. Los rechazos y fallos se registran por separado, de modo que puedan distinguirse de una clasificación sin riesgo.

La comprobación actual se ejecutó en Python 3.12.14 con biblioteca estándar. El motor se probó con reenvíos duplicados, revisiones tardías, saltos de secuencia, conflictos, datos inválidos, separación de llamadas, cierre, fallo y memoria acotada. Después se reprodujeron las entradas de la simulación de referencia. Comparar con ese cálculo permite detectar diferencias de implementación, aunque ambas versiones podrían compartir un supuesto incorrecto.

Antes de conectar la interfaz habrá que verificar otros puntos: una petición ambigua que se aclara después; el cambio de una negación en la transcripción; una respuesta de voz vacía; demora de procesamiento mayor que la cadencia; y cierre de la sesión mientras un fragmento sigue en espera. En cada caso se comprobará qué se mostró, cuándo y qué se conservó. Ninguna de esas pruebas con audio se declara ejecutada.

### F. Corpus previsto y comparación reservada
La guía de anotación definirá las llamadas legítimas y de riesgo y el final de la primera petición que justifica una advertencia, t0. Incluirá gestiones legítimas de pago o verificación para evitar que una palabra se confunda con una etiqueta de fraude. Un segundo revisor, cuando se confirme, anotará una muestra sin ver las alertas. Se informarán acuerdos de etiqueta y diferencias de las marcas de tiempo. Si persiste una duda, se analizará el conjunto con y sin ese caso.

El anteproyecto prevé unas 40 llamadas preliminares, 20 por clase, para revisar la guía y los tiempos. La meta del conjunto ampliado es de unas 500, cuya viabilidad depende de esa prueba. Se propone reservar 240 llamadas, 120 por clase, en al menos 12 familias ajenas al ajuste. Con 120 casos independientes, el semiancho nominal al 95 % de una proporción de 0,5 es aproximadamente 8,9 puntos porcentuales. Es una referencia de precisión; la correlación entre variantes puede ampliarlo y no constituye un cálculo de potencia.

Los guiones, sus paráfrasis y las voces reutilizadas se agruparán antes de separar entrenamiento, validación y reserva. El texto de prueba no se usará para construir el vocabulario ni para elegir parámetros. La reserva se abrirá con configuración fija. Si faltan familias o casos, se reportará el tamaño alcanzado y el contraste será exploratorio. Las 320 trazas de este corte sirven para verificar el análisis y no sustituyen ese corpus de llamadas.

### G. Generador y medidas de la prueba sintética
Se reutilizó el generador documentado en la primera versión, con semilla 20261116. Sus 16 familias ficticias tienen cinco llamadas por cada combinación de clase y perturbación, para un total de 320 llamadas y 2560 fragmentos. Cada fragmento dura dos segundos. En las de riesgo, t0 queda al cierre de los fragmentos 4, 5 o 6, lo que permite observar los cuatro segundos posteriores del análisis principal.

La evidencia de referencia se generó con una base de −0,45, efectos normales centrados por familia, llamada y fragmento (desviaciones de 0,20; 0,32 y 0,48) y un perfil añadido. Entre los casos de riesgo, los perfiles disperso, concentrado y débil tienen pesos de 0,55; 0,30 y 0,15. Los incrementos por posición y las probabilidades exactas están en configuracion.json. Entre las legítimas, el 45 % puede recibir un pico aislado uniforme de 1,10 a 1,90 y el 22 % de ese pico en el fragmento siguiente. Son supuestos del generador.

Se asignaron entre 8 y 20 palabras de referencia por fragmento como conteo, sin producir texto. Las probabilidades de sustitución, omisión e inserción son 0,06; 0,03 y 0,015 en baja perturbación, y 0,18; 0,10 y 0,05 en alta. Sustitución y omisión son excluyentes. Si e es la razón de errores por palabra, la evidencia perturbada es x − e + η, con η normal centrada y desviación 0,12 + 0,8e. La latencia generada suma 0,35 s, una variación uniforme de 0 a 0,25 s y otros 0,30 s en alta perturbación. No se midió un transcriptor.

La sensibilidad cuenta las llamadas de riesgo con algún aviso; la tasa de falsas alertas cuenta las legítimas con aviso, cada una sobre su clase. Se calculan también precisión, F1 y WER [13]. El WER sintético comprueba la fórmula, no la calidad del reconocimiento. Para oportunidad se usa la demora d = t_aviso − t0. Se consideran oportunas las primeras alertas entre 0 y 4 s, incluidas las fronteras. Las anteriores se separan como anticipadas, las posteriores como tardías y las ausentes como omisiones. Las omisiones no se convierten en cero segundos.

La demora se resume con mediana y percentil 95 de las detectadas. La diferencia por llamada se informa solo en las detectadas por ambas, con su denominador. En el ensayo integrado, t_aviso será el instante de presentación confirmado por la interfaz. En la prueba actual equivale al cierre del fragmento más la latencia sintética: no incluye medición del dibujado de pantalla.

Las diferencias se expresan como C menos F. Los intervalos del 95 % provienen de 4000 remuestreos de familias con reemplazo y semilla 20261117, manteniendo juntas las decisiones pareadas [14]. Se repitió el cálculo con umbrales de 1,00; 1,15 y 1,30 y plazos de 2, 4 y 6 s. El plazo de 6 s deja seguimiento incompleto en 50 casos de riesgo; sus conteos no sustituyen el contraste principal.

### H. Ética y criterio para la siguiente evaluación
Esta prueba no recogió voces, transcripciones ni datos personales. La futura incorporación de audio real requerirá revisar el protocolo institucional y el tratamiento aplicable. La Ley 1581 de 2012 regula la autorización y contempla los datos biométricos como sensibles [15]. El aplicativo analizará peticiones, sin identificar a las personas por su voz. Se documentarán el origen y la licencia de las voces sintéticas, y se detendrá el procesamiento si aparece un identificador real en material previsto como ficticio.

La etiqueta la define quien anota, lo que exige revisar sesgos. Una procedencia o un acento no será criterio de riesgo. Las observaciones sobre guiones y avisos podrán cuestionarse mediante la devolución. Si se incorporan participantes, se acordarán con ellos el acceso al material, su conservación y la devolución antes de recoger datos.

Antes de abrir la reserva se propone acordar con el director tres márgenes: considerar C si el límite inferior de la mejora de oportunidad supera 5 puntos porcentuales (pp), el límite superior del aumento de falsas alertas no supera 3 pp y el aumento de la mediana pareada no pasa de 1 s. Son márgenes para revisar, no requisitos ya aceptados por usuarios. Si la estimación es incierta o falta una condición, no se escogerá una regla por un solo indicador favorable.

## III. RESULTADOS DE LA COMPROBACIÓN
### A. Motor de referencia
Las ocho pruebas lógicas se completaron sin fallos. El ejemplo artificial de los cuatro puntajes produjo el primer aviso de C a los 6,5 s y de F a los 8,5 s. El reenvío de una entrada confirmada no añadió decisiones; una revisión tardía conservó la evidencia y la primera alerta originales. Los casos inválidos y fuera de orden se rechazaron sin clasificarlos.

Al reproducir las 320 trazas con evidencia de referencia y perturbada se registraron 10.240 decisiones. Se compararon 1280 primeros avisos: 320 llamadas por dos entradas y dos reglas. No hubo divergencias frente al cálculo de referencia. Esto verifica la correspondencia de las implementaciones para esas entradas. El resultado no comprueba por sí solo el desempeño del detector ni su ejecución en tiempo real.

### B. Contraste de las reglas con puntajes sintéticos
La Tabla II presenta los conteos del contraste principal. F emitió alguna alerta en 81 de 160 llamadas de riesgo y C en 68. Hubo 75 y 59 avisos oportunos. En las 160 legítimas, las falsas alertas fueron 24 y 8. Las dos reglas detectaron 56 casos de riesgo; 25 fueron detectados solo por F, 12 solo por C y 67 por ninguna. La precisión fue 77,1 % con F y 89,5 % con C; F1 fue 0,611 y 0,576.

@tabla contraste
Tabla II. Contraste sintético con umbral 1,15 y plazo de cuatro segundos.

@figura diferencias
Figura 2. Diferencias C menos F dentro de la simulación. Barras: intervalos del 95 % de 4000 remuestreos de las 16 familias ficticias.

La Tabla III separa los avisos por momento y muestra las omisiones. La mediana de las diferencias por llamada entre las 56 detectadas por ambas fue 0,00 s, con intervalo de remuestreo de 0,00 a 0,00 s. Las dos reglas deciden al cierre de ventanas discretas y comparten su latencia sintética. Las medianas calculadas sobre conjuntos distintos de llamadas fueron 0,71 y 2,40 s.

@tabla tiempos
Tabla III. Tiempo de las primeras alertas en 160 llamadas de riesgo sintéticas.

El WER simulado fue 21,9 %, con 7828 errores en 35.729 palabras de referencia generadas. Por condición fue 10,4 % y 33,5 %. Al perturbar la evidencia cambió la presencia de aviso en 42 de 320 llamadas con F y en 26 con C. Con baja perturbación se obtuvieron 45/80 y 40/80 avisos oportunos; con alta, 30/80 y 19/80. Los archivos conservan los resultados por familia y condición.

Manteniendo cuatro segundos, las diferencias de oportunidad C menos F fueron −5,0; −10,0 y −12,5 pp con umbrales de 1,00; 1,15 y 1,30. Las de falsas alertas fueron −11,3; −10,0 y −8,1 pp. La variación del plazo de dos a cuatro segundos, con umbral 1,15, pasó de 55 a 75 avisos oportunos para F y de 29 a 59 para C. No se excluyeron trazas ni se ajustaron los parámetros del generador para favorecer una regla.

## IV. DISCUSIÓN
### A. Magnitud e importancia para el aplicativo
El resultado principal de software es que el motor reproduce la decisión de referencia y permite explicar con qué datos apareció el primer aviso. La comprobación de duplicados, revisiones y orden aborda errores de integración que podrían distorsionar las métricas. Todavía falta comprobar que el usuario reciba el aviso en ese mismo instante: el motor no sustituye la medición de la interfaz.

En el escenario sintético, C tuvo 16 falsas alertas menos, pero también 16 avisos oportunos menos. Reducir interrupciones no basta si se pierden advertencias a tiempo. Tampoco basta restar las medianas de 0,71 y 2,40 s: provienen de grupos diferentes. En las detectadas por ambas, la mediana pareada fue cero. Para decidir una implementación importan los conteos, la demora por llamada y los casos que quedaron sin aviso.

### B. Incertidumbre y otras explicaciones
Los intervalos de la Tabla II no estiman el comportamiento en Colombia. Describen la variación de 16 familias artificiales. El número de trazas no vuelve representativos unos perfiles elegidos por diseño. De igual manera, la coincidencia de 1280 comparaciones verifica la reproducción de este cálculo, no una tasa de acierto del aplicativo.

La media ponderada puede amortiguar tanto una petición de riesgo concentrada como un pico legítimo. Esto ayuda a interpretar que C haya perdido avisos y reducido falsas alertas al mismo tiempo. La relación entre WER y puntuación fue impuesta y no describe qué sucede cuando se pierde una negación concreta. Además, la simulación comparte latencias y no reproduce el texto provisional. El intervalo de demora pareada concentrado en cero puede ser efecto de esos empates y de la discretización.

### C. Relación con los antecedentes y alcance
Lu y Chen encontraron ventajas para una votación semántica con otra regla, idioma y conjunto [8]; sus resultados no deciden qué historial debe conservar Centinela. La pregunta de Shen et al. sobre el momento de advertir [7] sigue vigente. Aquí se lleva a una especificación de software: puntaje confirmado, historial acotado, primera alerta y registro que no se reescribe después.

El motor permite separar esa decisión de los adaptadores de voz y del clasificador. Así se podrán localizar errores de transcripción, decisión o entrega del aviso, en vez de atribuirlos todos al modelo. Esa separación es la contribución de diseño del artículo. Su aplicación actual se limita a entradas numéricas válidas y ordenadas. La clasificación de conversaciones colombianas, la comprensión de los mensajes y el efecto en pérdidas reales siguen sin medirse.

### D. Condiciones para aceptar o cambiar el diseño
La integración deberá revisarse si la cadencia de dos segundos genera una cola persistente, si las correcciones tardías cambian muchas decisiones o si el contexto reduce alertas a tiempo en las familias reservadas. Esos casos podrían requerir cambiar la confirmación de texto, el historial o la interfaz. El cambio se documentará y se evaluará con otra reserva, sin retocar retrospectivamente las condiciones del contraste publicado.

En el ensayo con audio se decidirá con los márgenes acordados y sus intervalos, junto con una revisión de errores. Un resultado incierto o un aumento inadmisible de omisiones mantendrá abierta la comparación. Para pasar a llamadas con personas se necesitará además comprobar la comprensión del aviso y que la ausencia de alerta no se interprete como garantía de seguridad.

## V. CONCLUSIONES
Se especificó el mecanismo de alertas de Centinela y se implementó un motor de referencia para puntajes. La entrada confirmada, el historial por llamada y la conservación del primer aviso permiten reproducir la decisión sin que un reenvío o una corrección tardía cambien lo registrado. Las comprobaciones respaldan esa lógica en las trazas utilizadas.

La integración con audio sigue prevista. Whisper aportará la transcripción y el clasificador una evidencia común para ambas reglas; el ensayo tendrá que medir los errores y el momento real de presentación. Los resultados sintéticos no permiten elegir una estrategia para el aplicativo. Dejan un motor verificable y criterios para estudiar qué debe conservarse o cambiarse al construirlo.

## DISPONIBILIDAD Y CONTRIBUCIONES
El paquete adjunto conserva el generador y las trazas originales y añade el motor, sus pruebas y la auditoría de reproducción. Incluye configuración, diccionario, semillas, versiones y huellas SHA-256. CSV y JSON facilitan la lectura; el código propio se ofrece bajo MIT y los datos sintéticos bajo CC0. La organización sigue los principios FAIR [16] y la Política Nacional de Ciencia Abierta [17].

No hay DOI público en esta entrega. El material sintético no tiene una restricción de privacidad; su depósito con identificador persistente queda pendiente del autor. Mientras tanto, se adjunta el paquete y puede solicitarse al correo de correspondencia. No se afirma que el requisito de depósito externo esté completado. La revisión cruzada y la devolución también siguen previstas.

Mathew Pereira Uribe es el autor del anteproyecto y responsable de revisar y presentar esta adaptación. El Anexo A concreta la devolución; el Anexo B declara la ayuda de IA en código y redacción. No hubo participantes externos en la simulación.

## AGRADECIMIENTOS
Al docente Carlos Mauricio Blanco Muñoz por la orientación del anteproyecto. Esta comprobación no reporta financiación específica.

@referencias

@anexoA
## ANEXO A PLAN DE DEVOLUCIÓN
### Situación y destinatarios
La prueba de este corte se hizo con números generados, sin grabar voces ni consultar a víctimas. Compartiré los avances con el director del anteproyecto, el docente del taller y un equipo par. La devolución está por realizarse; busca discutir el diseño y sus límites, antes de probarlo con audio.

### Material y mensaje
Al director y al docente les entregaré el artículo, el esquema de la Figura 1 y una hoja sin fórmulas con los conteos de la Tabla II. El equipo par recibirá el borrador y las instrucciones para reproducir la comprobación. El mensaje será que el motor conserva la primera alerta y reproduce el cálculo con puntajes sintéticos, mientras que la calidad de la transcripción y la utilidad del aviso siguen pendientes.

En la hoja mostraré que el contexto redujo las falsas alertas de 24 a 8 entre 160 llamadas legítimas y también los avisos oportunos de 75 a 59 entre 160 de riesgo. Ningún porcentaje se presentará como desempeño en llamadas reales. Pediré revisar, además, qué debería mostrarse cuando falle el transcriptor y cómo explicar los casos sin advertencia.

### Responsable y fechas propuestas
Mathew Pereira Uribe. La revisión con el equipo par y la entrega al docente se proponen para el tercer corte, en noviembre de 2026, según el calendario del curso. Con el director se revisará al iniciar Trabajo de grado II, en febrero de 2027, antes de acordar los márgenes y abrir la reserva. Estas fechas son propuestas, no reuniones confirmadas.

### Observaciones y desacuerdos
Se podrán dejar comentarios en el PDF o escribir a mpereira17@ucatolica.edu.co. Llevaré una bitácora con fecha, autor de la observación, punto señalado, respuesta y cambio realizado. La siguiente versión se acompañará de esa bitácora para que se pueda comprobar qué se atendió.

Si una etiqueta sigue en duda tras revisar la petición del diálogo, se informará el análisis con y sin el caso. Los márgenes de decisión se acordarán con el director por escrito antes de abrir la reserva y se mantendrán durante esa prueba. El acento o la procedencia de quien habla no se usarán para resolver la etiqueta.

### Cómo se comprobará la utilidad de la devolución
Pediré al equipo par explicar qué se ejecutó, qué queda pendiente y proponer una mejora del diseño. Registraré qué observaciones distinguieron la simulación del ensayo con audio y cuáles provocaron cambios. Si no se reciben respuestas, quedará anotado sin dar por hecha la devolución. No se compartirán voces ni datos identificables.

@anexoB
## ANEXO B DECLARACIÓN DE USO DE IA GENERATIVA
El problema, los objetivos y la propuesta de Centinela vienen de mi anteproyecto de trabajo de grado. Se utilizó Claude (Anthropic) como apoyo en el generador de trazas y la revisión del texto. ChatGPT (OpenAI) ayudó a preparar el borrador y el código de simulación y, en esta adaptación, a desarrollar el motor de referencia, sus comprobaciones y la edición del artículo.

Los resultados se contrastaron con los archivos de salida, se reprodujeron las trazas con las semillas documentadas y se verificó la coincidencia del motor con el cálculo de referencia. No se usó IA para entrevistar o grabar personas. El uso de estas herramientas no sustituye mi revisión académica ni la validación del diseño con el director.
