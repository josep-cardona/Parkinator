### PARKINATOR

## El Problema
Todos hemos experimentado la frustración de dar vueltas interminables intentando aparcar cerca de nuestro destino. Sin embargo, este problema va mucho más allá de la simple pérdida de tiempo. Esta búsqueda constante no solo genera estrés y agotamiento mental en los conductores, sino que representa un grave problema medioambiental. Los vehículos que circulan durante largos periodos de tiempo buscando una plaza consumen recursos innecesarios y aumentan drásticamente las emisiones contaminantes en nuestras ciudades.

## La Solución
Desde Smooth Operators proponemos una solución innovadora basada en hardware. Mediante la implementación de sensores controlados por placas Arduino Uno, hemos creado un sistema de detección inteligente que identifica la disponibilidad de las plazas de aparcamiento. Nuestra plataforma optimiza el flujo de vehículos y asiste a los conductores para que encuentren sitio rápidamente. Gracias a esta eficiencia, logramos minimizar los kilómetros recorridos en vano, lo que se traduce en una reducción directa y significativa de las emisiones de gases contaminantes.

¿Cómo Funciona? (Arquitectura del Sistema)
Nuestro producto funciona bajo una infraestructura que conecta hardware IoT con una interfaz accesible para cualquier usuario. El sistema está formado por un bot de Telegram, que actúa como interfaz principal, conectado de forma remota a una red de microcontroladores Arduino equipados con cámaras (Vision Nodes). Estos nodos, distribuidos por la ciudad, son los encargados de analizar las calles mediante visión por computador para detectar las plazas de aparcamiento libres en tiempo real y enviar esta información directamente al dispositivo del conductor.

## Reconocimiento de Imagen (Prueba de Concepto a Escala)
Para el sistema de detección, hemos utilizado Edge Impulse para entrenar un modelo de Machine Learning capaz de identificar las plazas libres. Debido a las limitaciones de tiempo del hackathon y a la falta de un dataset real para entrenar el modelo, hemos diseñado una Prueba de Concepto (PoC) a escala muy efectiva:

El Entorno Simulado: Hemos creado una maqueta que representa una calle con sus plazas de aparcamiento y hemos utilizado patos de goma para simular los vehículos.

El Sistema de Detección: En el centro de cada plaza libre hemos dibujado un círculo naranja. Entrenamos nuestro modelo de visión por computador, proporcionando múltiples imágenes desde distintos ángulos, distancias y condiciones de iluminación, para que detecte específicamente estos puntos naranjas.

La Lógica: Si un coche (pato) aparca en la plaza, oculta el círculo naranja. Al no ser reconocido por la cámara, el modelo interpreta automáticamente que la plaza ha pasado a estar ocupada.

A pesar de ser un entorno simulado, esta estrategia nos ha permitido iterar rápidamente y conseguir un modelo altamente preciso, obteniendo un F1-Score aproximado del 92%. Gracias a esto, el nodo es capaz de contar con fiabilidad el número de plazas libres en su campo de visión.

## Flujo de Comunicación (Del Nodo al Usuario)
Para transmitir esta información en tiempo real sin saturar el sistema, hemos implementado una lógica basada en la proximidad:

El usuario contacta con el Nodo Central de nuestra red a través de Telegram y envía la dirección o las coordenadas a las que se dirige.

El Nodo Central procesa la ubicación e identifica cuáles son los Vision Nodes (los Arduinos con cámara en las calles) más cercanos a ese destino, filtrando mediante un radio máximo predefinido.

El usuario se "suscribe" automáticamente a estos Vision Nodes cercanos.

A partir de ese momento, los nodos le transmiten la cantidad exacta de plazas libres disponibles en sus respectivas calles, permitiendo al usuario elegir libremente y con antelación hacia dónde dirigirse.