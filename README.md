![alt text][logo]

[logo]: culebras.png "Los Culebra"

# Reto ocupa2

## El problema

La propuesta del reto es localizar los influencers en las redes sociales de Twitter e Instagram. El objetivo es encontrar a los usuarios que mejor se adapten dentro de unas categorías definidas por varios hashtag.

# La solución de los Culebra

Nuestra solución se basa en el concepto de karma, un valor numérico dependiente de cada categoría y por cada tipo de acción, de forma que podemos evaluar los usuarios por popularidad. Generamos un karma "global" para cada usuario que nos permite identificar los usuarios con más "influencia" dentro de cada categoría.

## Funcionalidades

El sistema interactua con Instagram y Twitter, realizando varias acciones con cada una de ellas:

- Descarga de los datos y generación de un grafo de interacciones. Esto de por si no es útil para el usuario final pero es lo que permite realizar los análisis y tomar decisiones.
- Follows automáticos. El sistema realiza follows y unfollows automáticos de usuarios basandose en criterios de efectividad del mensaje mediante el karma.
- Likes automáticos. Se detectan posts "interesantes" y se dan likes. El criterio para detectar un post interesante está basado en la popularidad del usuario que lo publica. Al basarse en la popularidad de los usuarios muchos de esos Like pueden darse a usuarios que no se siguen (que se decide por karma), lo que genera una interacción más orgánica (en lugar de dar Like simplemente a los que se consideran populares como para seguir)
- Registro de las acciones. Las acciones quedan registradas en una tabla de eventos.
- Panel de control que permite visualizar las acciones y ciertas estadísticas.

## Arquitectura

Se trata de una aplicación Django 2.1 escrita en Python 3.7 usando Neo4J como base de datos ya que nos permite almacenar y analizar relaciones de una forma más natural y potente que las bases de datos SQL o de documentos .

# El karma

Para el cálculo del karma nos hemos basado en la fórmula de valoración de riesgo del [ratio de Sharpe](https://web.stanford.edu/~wfsharpe/art/sr/sr.htm) sólo que en lugar de rentabilidad usamos la mediana del número de interacciones de los posts. Puesto que los mock de las API no permiten dar el número de seguidores de todas las redes sociales (en el caso de Twitter) utilizamos un valor de referencia medio de 0, pero se debería usar posiblemente algo similar a un 1% del número de seguidores.

Eso implicaría que tener menos de 1% de likes respecto al número de seguidores alimentaría un "mal karma" mientras que mejorar ese valor aumentaría el karma.

![Sharpe ratio formula][sharpe]

[sharpe]: https://wikimedia.org/api/rest_v1/media/math/render/svg/f5f2465eebaadbf656a6dfc8ea1002f68a5c5739 "formula de sharpe"

La fórmula de cálculo de karma podría ser ajustada si se quisieran tener en cuenta otros valores, pero eso es discutido más adelante en la sección sobre Posibles mejoras.

## El límite de requests

# Posibles mejoras

## Eficiencia

En esta solución las tareas son monohilo, con lo que pueden tardar varios minutos en funcionar, una posible mejora sería hacer que las tareas fueran multihilo (muy sencilo usando async de forma nativa ya que las tareas son I/O) pero creemos que la ganancia no sería importante puesto que la mayor limitación se encuentra en el número de peticiones que cada red social permite.

## Datos más ajustados a la realidad

Nuestra apuesta por una base de datos de grafos como Neo4J se inspira que los datos importantes 

Desgraciadamente los mock de las API no ofrecían datos que relacionaran los usuarios entre sí (follow) o con posts (like,  comentar o responder, retweet) pero si se pudieran obtener esos datos sería posible guardarlos en forma de grafo y usando el lenguaje de query de [Neo4J y sus sistemas de visualización](https://neo4j.com/developer/cypher-query-language/) nos permitiría análisis más complejos como:

- Qué usuarios interactuan con usuarios que interesan.
- Identificar usuarios cuyas respuestas tienen más interacción (p.e. aquellos posts en los que los comentarios obtienen más likes)

## Datos temporales

Relacionado con lo anterior, si existieran marcas temporales de cuando se producen las interacciones (p.e. cuando un usuario hizo un like) sería posible añadir esas marcas temporales como propiedades de cada relación que permitirían ponderar las interacciones al realizar las consultas.

## Karma

Teniendo los datos sobre interacción de usuarios se debería aplicar otro función para el cálculo del karma, dudamos de que el ratio de Sharpe fuera aplicable y deberían evaluarse otros modelos que valorasen las relaciones entre los distintos nodos y sus relaciones, seguramente la opción planteada tendría una obvia inspiración del [algoritmo PageRank usado por Google](https://www.youtube.com/watch?v=b3fwA3EWCd8).

## Análisis del mensaje

En caso de que se pudiera acceder al texto de los posts se podrían analizar sus mensajes con técnicas de Procesamiento del Lenguaje Natural y los resultados de esos análisis deberían influir en el comportamiento del sistema, por ejemplo el cambio más simple sería sólo dar likes a mensajes de tono positivo.