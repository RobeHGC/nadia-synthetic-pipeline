# GUIDELINES.md - Guía de Etiquetado Proyecto Nadia v2.0

## Introducción
El proposito es explicar las definiciones de las etiquetas, proponer jerarquías entre ellas y posibles situaciones díficiles.

## Proceso de Etiquetado
1. Leer el mensaje completo
2. Identificar la intención DOMINANTE
3. Evaluar el tono independientemente del contenido
4. Clasificar nivel de seguridad (ante la duda, elegir el más alto)
5. En caso de ambigüedad, consultar el "Libro de Casos Difíciles"

## Dimensiones y Definiciones

### 0. Dimensión: profile_id (Arquetipo de Comportamiento)

Propósito: Definir la personalidad fundamental del usuario para guiar la estrategia de comunicación general. Se asigna una vez por conversación, usualmente tras los primeros mensajes.

Etiquetas a Definir:
#### 0.1 PROFILE_1_DIRECTO: [Definición, ejemplos]
#### 0.2 PROFILE_2_HESITANTE: [Definición, ejemplos].
#### 0.3 PROFILE_3_DECEPCIONADO: [Definición, ejemplos].

Método de Asignación: Será asignado por un modelo clasificador (Enrutador de Intenciones) o manualmente en las primeras fases.

### 1. PRIMARY_INTENT
#### 1.1 GREETING
Definición: Apertura de conversación o saludo inicial.
Ejemplos positivos:

"Hola"
"Hey hermosa"
"Buenas noches, ¿cómo estás?"

Ejemplos negativos:

"Hola, ¿cuánto cuestas?" → TRANSACTIONAL_INQUIRY (tiene saludo pero la intención dominante es transaccional)
"Hey otra vez" → SMALL_TALK (es una continuación, no apertura)

Regla de decisión: Si contiene saludo + otra intención, clasificar según la intención dominante.

#### 1.2 TRANSACTIONAL_INQUIRY
Definición: Preguntas sobre precios, servicios, links o mecánica del negocio.
Ejemplos positivos:

"¿Cuál es el link?"
"¿Cuánto cuesta tu Fanvue?"
"¿Cómo funciona esto?"
"¿Aceptas PayPal?"

Ejemplos negativos:

"¿Vale la pena?" → HESITATION_OR_OBJECTION
"¿Por qué debería pagar?" → HESITATION_OR_OBJECTION

Regla de oro: Si menciona dinero/pago/plataforma = TRANSACTIONAL

#### 1.3 RELATIONAL_QUESTION
Definición: Preguntas que buscan conocer aspectos personales o crear conexión emocional.
Ejemplos positivos:

"¿Qué te gusta hacer?"
"¿Eres real?"
"¿Tienes novio?"
"¿Qué buscas en un hombre?"

Ejemplos negativos:

"¿Qué hora es allá?" → SMALL_TALK
"¿Hablas español?" → SMALL_TALK (es funcional, no relacional)

Test rápido: ¿La respuesta revelaría algo personal/emocional? Sí = RELATIONA

#### 1.4 HESITATION_OR_OBJECTION
Definición: Expresión de duda, resistencia o necesidad de convencimiento sobre el funnel.
Ejemplos positivos:

"No sé si vale la pena"
"¿Por qué no podemos hablar aquí?"
"Parece caro"
"¿Es seguro?"

Ejemplos negativos:

"No me gustas" → NEGATIVE_FEEDBACK
"Prefiero conocerte primero" → RELATIONAL_QUESTION

Clave: Buscar palabras como "pero", "no sé", "¿por qué debo...?"

#### 1.5 COMPLIMENT
Definición: Halagos, cumplidos o expresiones de atracción.
Ejemplos positivos:

"Eres hermosa"
"Me encantas"
"Qué sonrisa tan linda"
"Eres perfecta"

Ejemplos negativos:

"Me gustas, ¿tienes WhatsApp?" → TRANSACTIONAL_INQUIRY (el cumplido es secundario)
"Bella, ¿cómo estás?" → GREETING (el cumplido es parte del saludo)

#### 1.6 PERSONAL_SHARE
Definición: Usuario comparte información personal no solicitada.
Ejemplos positivos:

"Acabo de divorciarme"
"Trabajo en construcción"
"Estoy solo desde hace meses"
"Tengo 45 años y dos hijos"

Ejemplos negativos:

"Soy de México" → SMALL_TALK (respuesta a pregunta implícita)
"También me gusta la música" → SMALL_TALK (es reactivo, no proactivo)

#### 1.7 SMALL_TALK

Definición: Conversación casual, funcional o de bajo impacto emocional que mantiene el canal de comunicación abierto pero no busca una conexión profunda. Incluye preguntas logísticas o respuestas a ellas. Es un comportamiento común pero que debe distinguirse de las preguntas que buscan una conexión real.

Ejemplos positivos:
"¿De dónde eres?"
"¿Qué hora es allá?"
"Aquí está lloviendo."
"Yo también soy de México." (Como respuesta a una pregunta).
"Hey otra vez."

Ejemplos negativos:
"Hola, ¿cómo estás?" → GREETING. Esta es la apertura formal de una conversación.
"¿Qué te apasiona en la vida?" → RELATIONAL_QUESTION. Esta pregunta busca explícitamente una conexión emocional más profunda, clave para el "Perfil 2: El Hesitante". 
Test rápido: ¿Se podría tener esta misma conversación con un conocido o un extraño en un ascensor para llenar el silencio? Si la respuesta es sí, es muy probable que sea SMALL_TALK.

#### 1.8 NEGATIVE_FEEDBACK
Definición: El usuario expresa una queja, crítica, enojo, frustración o rechazo explícito hacia el bot, la interacción o el modelo de negocio.  La intención es confrontar o expresar descontento, y es el comportamiento típico del "Perfil 3: El Decepcionado". 

Ejemplos positivos:
"Hablar contigo es aburrido."
"Siempre dices lo mismo, pareces un robot."
"Ah, o sea que al final solo quieres mi dinero. Qué decepción."
"Esto es una estafa."

Ejemplos negativos:
"No sé si vale la pena" → HESITATION_OR_OBJECTION. Esto es una expresión de duda, no una queja o crítica directa.
"No me responden los mensajes" → TECHNICAL_ISSUE. Esto es un reporte de un fallo técnico, no una crítica a la personalidad o al modelo de negocio.
Regla de decisión: La emoción dominante es la decepción, el enojo o la crítica directa. No busca resolver una duda (como HESITATION_OR_OBJECTION), sino sentenciar un hecho negativo. Es la señal principal para activar la estrategia de "De-escalada y Contención Segura". 

#### 1.9 TECHNICAL_ISSUE
Definición: El usuario reporta un problema técnico con el bot, la plataforma, un link o un proceso de pago. Su intención es buscar soporte.
   * Ejemplos positivos:
      * "El link que me mandaste no funciona."
      * "Intenté unirme pero me sale un error 404."
      * "No me llegan tus notificaciones."
   * Ejemplos negativos:
      * "¿Por qué es tan caro?" → HESITATION_OR_OBJECTION (Es una objeción al precio, no un fallo técnico).
      * "Tu respuesta tarda mucho en llegar." → NEGATIVE_FEEDBACK (Es una crítica a la calidad del servicio, no un reporte de error).
   * Regla de decisión: El usuario describe una acción que intentó realizar y que falló por una razón técnica.
#### 1.10 FANTASY_ROLEPLAY
Definición: El usuario intenta llevar la conversación a un escenario de fantasía o ficción, invitando a Nadia a asumir un rol o actuando él mismo uno.
* Ejemplos positivos:
   * "te abrazo y te doy un beso"
   * "Imagina que estamos casados y llegas a casa del trabajo..."
   * "Actúa como si fueras mi novia celosa."
* Ejemplos negativos:
   * "Quiero que seas mi novia." → RELATIONAL_QUESTION (Es un deseo, no el inicio de un acto de roleplay).
   * "Eres una diosa." → COMPLIMENT (Es un halago, no un escenario de fantasía).
* Regla de decisión: Busca verbos que establezcan un marco ficticio ("imagina que", "actúa como si") o acciones descritas en tercera persona o asteriscos.  
#### 1.11 GOODBYE
Definición: El usuario señala de manera explícita su intención de terminar la conversación por el momento.
      * Ejemplos positivos:
         * "Bueno, me voy a dormir. Hablamos mañana."
         * "Adiós, que descanses."
         * "Luego seguimos hablando."
      * Ejemplos negativos:
         * "Ok." → DISMISSIVE (Es un tono, no una despedida formal).
         * "Ya no quiero hablar contigo." → NEGATIVE_FEEDBACK (El foco es el rechazo, no la despedida cortés

### 2. MESSAGE_TONE
#### 2.1 FRIENDLY
Definición: Tono amigable, abierto y positivo.
Indicadores: Emojis positivos, lenguaje cálido, preguntas abiertas.
Ejemplo: "Hola! Me encantaría conocerte mejor 😊"

#### 2.2 ENGAGED
Definición: Alto interés, participación activa en la conversación.
Indicadores: Preguntas de seguimiento, respuestas elaboradas, entusiasmo.
Ejemplo: "Wow, ¿en serio te gusta el rock? Yo toco guitarra desde los 15"
#### 2.3 SKEPTICAL
Definición: Dudoso pero no hostil, necesita convencimiento.
Indicadores: Preguntas de verificación, "no sé", "tal vez".
Ejemplo: "Mmm no sé, ¿cómo sé que eres real?"
#### 2.4 FRUSTRATED
Definición: Molestia o impaciencia evidente.
Indicadores: Lenguaje seco, críticas, impaciencia.
Ejemplo: "Ya te pregunté 3 veces y no me respondes"
#### 2.5 DISMISSIVE
Definición: Desinterés o rechazo sin hostilidad.
Indicadores: Respuestas cortas, evasivas, "ok", "ya".
Ejemplo: "Ok", "No gracias", "Paso"

### 3. SAFETY_LEVEL
Propósito: Clasificar cada mensaje según su nivel de riesgo para la seguridad, la reputación y el cumplimiento legal. Es el input crítico para la Constitution (Capa 4).

#### 3.1 LEVEL_0_SAFE
Definición: Conversación completamente normal sin contenido sensible, romántico o sugestivo.
Ejemplos positivos:

"Hola, ¿cómo estás?"
"¿De dónde eres?"
"Me gusta la música pop"
"¿Cuál es tu comida favorita?"

Indicadores clave:

Preguntas generales
Small talk
Información factual
Ausencia total de contenido romántico/sexual

#### 3.2 LEVEL_1_FLIRT_SAFE
Definición: Coqueteo ligero y aceptable, cumplidos románticos, humor juguetón que no cruza líneas.
Ejemplos positivos:

"Eres muy bonita"
"Me encanta hablar contigo 😊"
"Tienes una sonrisa hermosa"
"¿Tienes novio?"
"Me gustas mucho"

Ejemplos negativos:

"Quiero verte sin ropa" → LEVEL_2_BORDERLINE
"Eres sexy" → Depende del contexto, puede ser LEVEL_2

Regla: Si es algo que dirías en una primera cita en un lugar público, es LEVEL_1.

#### 3.3 LEVEL_2_BORDERLINE
Definición: Lenguaje sugestivo, insinuaciones sexuales veladas, contenido que requiere una respuesta muy cuidadosa para desviar o de-escalar.
Ejemplos positivos:

"¿Qué llevas puesto?"
"Quisiera estar ahí contigo en tu cama"
"Cuéntame tus fantasías"
"Eres muy sexy"
"te beso apasionadamente"
"¿Qué harías si estuviera ahí?"

Estrategia requerida: Nadia debe responder de forma que desvíe elegantemente sin ser brusca ni alentar.
Respuesta ejemplo: "Ay qué lindo eres 😊 Mejor cuéntame, ¿qué planes tienes para hoy?"

#### 3.4 LEVEL_3_INAPPROPRIATE
Definición: Contenido explícitamente sexual, acoso, amenazas, lenguaje vulgar, solicitudes inapropiadas. Requiere terminación inmediata de la conversación o respuesta de seguridad predefinida.
Ejemplos positivos:

Descripciones explícitas de actos sexuales
Lenguaje vulgar o degradante
"Muéstrame tus [partes del cuerpo]"
Amenazas de cualquier tipo
Insistencia después de un "no"
Contenido ilegal

Ejemplos negativos:

"Eres sexy" → LEVEL_2_BORDERLINE (no es explícito)
"No me gustas" → LEVEL_0_SAFE con NEGATIVE_FEEDBACK

Acción requerida: Respuesta genérica de seguridad + posible bloqueo.
Reglas de Escalamiento

Ante la duda, escalar: Si no estás seguro entre dos niveles, elige el más alto.
El contexto importa:

"Quiero conocerte" → LEVEL_0_SAFE
"Quiero conocerte... íntimamente 😏" → LEVEL_2_BORDERLINE


Acumulación: Múltiples mensajes LEVEL_1 en secuencia rápida pueden indicar que se debe tratar como LEVEL_2.
Palabras clave de alerta:

LEVEL_2: "sexy", "caliente", "fantasías", "juntos", "cama"
LEVEL_3: palabras vulgares, partes del cuerpo, verbos sexuales explícitos
#### matriz de decisión rapida

| Si el mensaje contiene…                     | Entonces SAFETY_LEVEL es       |
|---------------------------------------------|--------------------------------|
| Solo preguntas generales o small talk       | LEVEL_0_SAFE                   |
| Cumplidos sobre belleza/personalidad        | LEVEL_1_FLIRT_SAFE             |
| La palabra "sexy" o insinuaciones           | LEVEL_2_BORDERLINE             |
| Lenguaje sexual explícito                   | LEVEL_3_INAPPROPRIATE          |
| Amenazas o acoso                            | LEVEL_3_INAPPROPRIATE          |

### 4. DIMENSIÓN: CUSTOMER_STATUS
Propósito: Modelar la etapa del ciclo de vida comercial del usuario. Esta dimensión se asigna a nivel de conversación completa, NO mensaje individual.
No se etiquetaran en docker, se etiquetará a nivel global 

#### 4.1 PROSPECT
Definición: Usuario nuevo que nunca ha expresado intención de pagar ni ha sido expuesto a un CTA directo.
Indicadores:

Primera conversación o primeras interacciones
No ha preguntado sobre precios
No ha sido dirigido a plataformas de pago
Puede estar en cualquier rapport_stage inicial

Ejemplos de comportamiento:

Hace preguntas generales
Envía cumplidos
Busca conocer a Nadia

#### 4.2 LEAD_QUALIFIED
Definición: Usuario que ha mostrado interés comercial (preguntó precios, mostró curiosidad sobre el servicio) O ha recibido un CTA pero aún no convierte.
Indicadores:

Ha preguntado "¿cuánto cuesta?"
Ha recibido información sobre Fanvue/links
Ha expresado hesitación ("no sé si vale la pena")
Está considerando la decisión

Transición desde PROSPECT: Cuando pregunta sobre precios O cuando Nadia presenta el primer CTA suave.

#### 4.3 CUSTOMER
Definición: Usuario que ha realizado al menos una transacción de pago o se ha suscrito a la plataforma paga.
Indicadores:

Confirmó haberse unido a Fanvue
Menciona haber pagado
Hace preguntas sobre contenido exclusivo
Interacciones post-conversión

Nota: En el contexto actual donde no tienes integración directa, esto se infiere del contexto conversacional.

#### 4.4 CHURNED
Definición: Usuario que era CUSTOMER pero canceló, dejó de pagar, o expresó explícitamente que no continuará.
Indicadores:

"Cancelé mi suscripción"
"Ya no voy a pagar más"
Era customer pero lleva tiempo sin interactuar
Expresó insatisfacción post-compra

Importante: PROSPECT que dice "no me interesa" NO es CHURNED, simplemente permanece como PROSPECT.

#### 4.5 LEAD_EXHAUSTED 
Definición: Usuario que ha demostrado un patrón consistente de buscar interacción gratuita sin intención de conversión a pesar de múltiples oportunidades presentadas.
Indicadores Conductuales:

Ignora o rechaza sutilmente los CTAs ("tal vez después", "no ahora")
Mantiene conversaciones largas pero evita temas comerciales
Puede intentar mover la conversación a plataformas gratuitas (whatsapp)
Patrones de "amor platónico" - mucha inversión emocional, cero inversión económica
##### Automático vía "Guardian de Recursos"
Asignar LEAD_EXHAUSTED cuando:
1. Estado actual == LEAD_QUALIFIED
2. cta_presented_count >= 3
3. cta_positive_response_count == 0
4. total_interactions > 20
5. (days_active_since_last_cta > 7 OR soft_rejections >= 2)

##### Donde soft_rejection incluye:
###### - "maybe later", "tal vez después"
###### - "no tengo dinero ahora"
###### - cambio de tema cuando se menciona pago
###### - "¿no podemos hablar aquí?"
Estrategia Aplicable:

Respuestas más cortas y menos personalizadas
CTAs solo cuando muestren señales claras de HIGH_INTENT
Posible uso de respuestas semi-automatizadas
Prioridad baja en cola de atención

Transiciones Válidas:

→ CUSTOMER (si finalmente convierte)
→ CHURNED (si expresa rechazo definitivo)
→ LEAD_QUALIFIED (si muestra renovado interés comercial después de período de enfriamiento)

### 5. DIMENSIÓN: RAPPORT_STAGE
Propósito: Medir la profundidad emocional y el nivel de conexión en la conversación. Modela la progresión natural de una relación.

#### 5.1 ICE_BREAKER
Definición: Etapa inicial de primer contacto. Las interacciones son superficiales y exploratorias.
Indicadores:

Primeros 3-5 mensajes de una conversación
Saludos, presentaciones
Preguntas básicas ("¿cómo estás?", "¿de dónde eres?")
Tono formal o cauteloso

Duración típica: 2-5 intercambios
Transiciones válidas:

→ RAPPORT_BUILDING (evolución natural)
→ CLOSING (si hay rechazo inmediato)

#### 5.2 RAPPORT_BUILDING
Definición: Construcción activa de conexión. El usuario muestra interés genuino y las conversaciones se vuelven más personales.
Indicadores:

Preguntas sobre gustos, intereses, vida personal
Usuario comparte información sobre sí mismo
Uso de humor, emojis
Conversaciones más largas y elaboradas
Cumplidos frecuentes

Ejemplos:

"¿Qué te gusta hacer en tu tiempo libre?"
"Yo también amo la música, toco guitarra"
"Me caes muy bien"

Transiciones válidas:

→ DEEP_EMOTION (profundización natural)
→ HIGH_INTENT (si aparecen señales fuertes)
→ CLOSING (si pierde interés)
→ ICE_BREAKER (reset si vuelve después de tiempo)

#### 5.3 DEEP_EMOTION
Definición: Conexión emocional establecida. El usuario comparte vulnerabilidades, sentimientos profundos o busca apoyo emocional.
Indicadores:

Comparte problemas personales
Expresa sentimientos hacia Nadia
Conversaciones sobre soledad, relaciones pasadas
Busca consuelo o comprensión
Mensajes largos y reflexivos

Ejemplos:

"Me siento muy solo últimamente"
"Nunca conocí a alguien como tú"
"Mi divorcio me dejó destrozado"
"Contigo me siento especial"

Transiciones válidas:

→ HIGH_INTENT (natural tras conexión profunda)
→ RAPPORT_BUILDING (puede retroceder si se siente vulnerable)
→ CLOSING (si se agota emocionalmente)

#### 5.4 HIGH_INTENT
Definición: Usuario muestra alta inversión emocional y/o intención transaccional. Es el momento óptimo para CTAs.
Indicadores:

Expresiones fuertes de deseo/necesidad
"Necesito verte", "No puedo dejar de pensar en ti"
Preguntas sobre exclusividad
Iniciativa para profundizar la relación
Responde rápidamente y con entusiasmo

Ejemplos:

"¿Podemos hablar más seguido?"
"Quiero conocerte mejor"
"¿Dónde más podemos hablar?"
"Eres muy especial para mí"

Transiciones válidas:

→ CLOSING (natural tras conseguir objetivo o rechazo)

#### 5.5 CLOSING
Definición: Etapa de cierre, ya sea temporal (despedida) o permanente (rechazo).
Indicadores:

Despedidas explícitas
Rechazo a propuestas
Disminución drástica en la frecuencia/longitud de mensajes
Expresiones de desinterés

Tipos:

Cierre positivo: "Hablamos mañana, descansa"
Cierre negativo: "No me interesa, adiós"
Cierre neutral: "Ok, bye"

Transiciones válidas:

→ ICE_BREAKER (si retoma conversación posteriormente)
Estado terminal si es cierre definitivo

### 6. TEMPORAL_CONTEXT

### Atributos del Perfil de Usuario"
Esta sección describe los atributos estáticos o semi-estáticos que se almacenan para cada usuario. A diferencia de las dimensiones de mensaje, estos atributos se asignan una vez o se actualizan con poca frecuencia.

#### user_id: Identificador único.
#### profile_id: Arquetipo de comportamiento asignado a nivel de conversación.
#### customer_status: Etapa del ciclo de vida, actualizada por reglas de negocio.
#### user_country
Descripción: País de origen del usuario, obtenido durante la conversación.
Método de Asignación: Extracción de información de la conversación. (Inicialmente manual o con una función simple, en el futuro podría ser un modelo de Named Entity Recognition).
#### user_occupation
Descripción: Profesión o a qué se dedica el usuario.
Método de Asignación: Extracción de información de la conversación

#### CASOS ESPECIALES Y ACLARACIONES

Conversaciones que retoman: Si un usuario vuelve después de días/semanas, evaluar si mantener el rapport_stage anterior o resetear a ICE_BREAKER.
Velocidad de progresión: Algunos usuarios pueden moverse rápidamente (ICE_BREAKER → RAPPORT_BUILDING en 3 mensajes), otros lentamente (20+ mensajes).
Señales de transición:

ICE_BREAKER → RAPPORT_BUILDING: Primera pregunta personal genuina
RAPPORT_BUILDING → DEEP_EMOTION: Primera vulnerabilidad compartida
DEEP_EMOTION → HIGH_INTENT: Expresiones de necesidad/deseo fuerte
Cualquier → CLOSING: Despedida o rechazo explícito

#### Reglas adicionales
1. No se puede saltar etapas (ej: ICE_BREAKER → HIGH_INTENT)
2. El retroceso es posible solo desde RAPPORT_BUILDING y DEEP_EMOTION
3. HIGH_INTENT es unidireccional hacia CLOSING
4. Después de CLOSING, solo se puede ir a ICE_BREAKER si pasa tiempo significativo




## Libro de Casos Difíciles
Caso 1: "Hola hermosa, ¿cuánto cuesta?"

PRIMARY_INTENT: TRANSACTIONAL_INQUIRY (la pregunta de precio domina)
MESSAGE_TONE: FRIENDLY (el "hermosa" indica tono positivo)
Lección: En mensajes mixtos, la intención > el saludo

### Caso 2: "No sé si eres real, pero me gustas"

PRIMARY_INTENT: HESITATION_OR_OBJECTION (la duda es el foco)
MESSAGE_TONE: ENGAGED (el "me gustas" muestra interés)
Lección: Hesitación + cumplido = todavía es hesitación

### Caso 3: "😍😍😍"

PRIMARY_INTENT: COMPLIMENT (expresión pura de atracción)
MESSAGE_TONE: ENGAGED (alto interés emocional)
Lección: Los emojis solos pueden expresar intención

### Caso 4: "Ya vi que cobras, adiós"

PRIMARY_INTENT: NEGATIVE_FEEDBACK (rechazo al modelo de negocio)
MESSAGE_TONE: DISMISSIVE (se está yendo)
Lección: Mencionar precio + rechazo = NEGATIVE_FEEDBACK, no TRANSACTIONAL

### Caso 5: El Ansioso/Suplicante

Mensaje: "Contéstame por favor...", "sigues ahí? 🥺", "no me dejes así"
Etiquetas:
primary_intent: NEGATIVE_FEEDBACK (La queja implícita es "me estás ignorando").
message_tone: ENGAGED o FRIENDLY (A pesar de la queja, el tono muestra un alto interés en continuar la conexión).
Lógica para Nadia: ¡Esta es una señal de oro! El usuario tiene una alta inversión emocional. Es un "Perfil 2: Hesitante" que teme perder la conexión. Es el momento perfecto para una respuesta que refuerce el rapport.

### Caso 6: El Impaciente/Enojado

Mensaje: "¿Por qué no contestas?", "llevo esperando 10 minutos", "vas a contestar o no?"
Etiquetas:
primary_intent: NEGATIVE_FEEDBACK
message_tone: FRUSTRATED
Lógica para Nadia: Esto es una señal de riesgo. El usuario está frustrado y podría convertirse en un "Perfil 3: Decepcionado". La respuesta debe ser rápida, conciliadora y eficiente.

## Transiciones válidas: "Filtro de Verosimilitud Emocional"
### RAPPORT 
= {
    'ICE_BREAKER': ['RAPPORT_BUILDING', 'CLOSING'],
    'RAPPORT_BUILDING': ['DEEP_EMOTION', 'HIGH_INTENT', 'CLOSING', 'ICE_BREAKER'],
    'DEEP_EMOTION': ['HIGH_INTENT', 'RAPPORT_BUILDING', 'CLOSING'],
    'HIGH_INTENT': ['CLOSING'],
    'CLOSING': ['ICE_BREAKER']  # Solo si reinicia conversación
}

### CUSTOMER_STATUS_TRANSITIONS 
= {
    'PROSPECT': ['LEAD_QUALIFIED'],
    'LEAD_QUALIFIED': ['CUSTOMER', 'LEAD_EXHAUSTED', 'PROSPECT'],
    'LEAD_EXHAUSTED': ['CUSTOMER', 'CHURNED', 'LEAD_QUALIFIED'],
    'CUSTOMER': ['CHURNED'],
    'CHURNED': []  # Estado terminal
}

## Matriz de Decisión Rápida
| Si el mensaje contiene... | Entonces PRIMARY_INTENT es... |
|--------------------------|------------------------------|
| Precio, costo, pago | TRANSACTIONAL_INQUIRY |
| "No sé si...", "pero..." | HESITATION_OR_OBJECTION |
| Información personal no solicitada | PERSONAL_SHARE |
[etc...]

## Changelog
- v2.0 (16/06/2025 11:29 pm): Versión inicial completa
- v2.1 (fecha): Añadidos casos X, Y, Z tras primera revisión