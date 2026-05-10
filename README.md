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

Instalación y Uso
Para desplegar y utilizar nuestra red de detección inteligente de aparcamiento, sigue los pasos a continuación. El sistema está diseñado para ser Plug & Play una vez cargado el código en los microcontroladores.

Requisitos Previos
Hardware:

Mínimo 2x placas Arduino (p. ej. Arduino Uno). Se configurará una como Main Node (nodo central) y otra como Vision Node (nodo de visión).

1x Módulo de cámara compatible, conectado directamente al Vision Node.

Software:

Arduino IDE instalado en tu ordenador.

La aplicación de Telegram (móvil o escritorio) para interactuar con el sistema.

Configuración del Sistema
Posicionamiento del Hardware: Coloca la cámara conectada al Vision Node en un punto elevado o estratégico que tenga una línea de visión clara y sin obstáculos hacia las plazas de aparcamiento que deseas monitorizar (en nuestro caso, la maqueta con los puntos naranjas).

Despliegue del Código:
Abre el Arduino IDE, crea un nuevo proyecto e importa el código de este repositorio. Carga el script correspondiente del Main Node en la primera placa, y el script del Vision Node (que incluye el modelo de Edge Impulse) en la segunda placa con la cámara.

Inicio de la Red:
Una vez alimentados, los Arduinos se conectarán automáticamente formando la red. El Vision Node comenzará a analizar las imágenes y a comunicarse con el Main Node.

Instrucciones de Uso (Bot de Telegram)
Para que el usuario final pueda interactuar con el sistema de forma intuitiva, hemos creado un bot de Telegram.

Abre Telegram y busca nuestro bot oficial: Parkinator_bot.

Inicia un chat y utiliza los siguientes comandos básicos para gestionar tu aparcamiento:

/park [dirección]: Envía este comando seguido de la dirección a la que te diriges (por ejemplo, /park Calle Falsa 123). El sistema buscará el Vision Node más cercano a esa ubicación y te suscribirá a sus actualizaciones, enviándote información en tiempo real sobre las plazas libres.

/cancel: Utiliza este comando una vez hayas aparcado o si deseas detener la búsqueda. El bot te desuscribirá del nodo y dejarás de recibir actualizaciones sobre las plazas disponibles.

Siguientes Pasos 
Nuestro principal objetivo a futuro es llevar este prototipo (Proof of Concept) a entornos urbanos reales. Para lograrlo, la prioridad será entrenar nuestro modelo de Inteligencia Artificial utilizando un dataset mucho más extenso, diverso y representativo, que incluya vehículos reales bajo distintas condiciones climáticas y de iluminación.
Además, proyectamos escalar el sistema horizontalmente implementando múltiples Vision Nodes en una misma calle. Disponer de diferentes perspectivas y ángulos de visión nos permitirá cruzar datos, reducir los puntos ciegos y aumentar drásticamente la precisión y certeza de la información que ofrecemos a nuestros usuarios.
