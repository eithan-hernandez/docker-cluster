
# Configuración de Clúster de Apache Spark en Docker Swarm

Este documento explica de forma extensa y detallada cómo configurar un clúster de Apache Spark usando Docker Swarm en una ASUS TUF Gaming F15, que actuará como nodo manager y también ejecutará contenedores worker y Jupyter Notebook para PySpark. Además, se incluyen consideraciones para escalar el clúster y conectar más computadoras en la LAN en el futuro.

## Requisitos

- **Hardware (ASUS TUF Gaming F15):**
  - CPU: Intel Core i5‑11400H (6 núcleos / 12 hilos)
  - RAM: 24 GB
  - GPU: NVIDIA RTX 2060 (opcional, para aceleración con CUDA)
- **Software:**
  - Docker Engine (v27.5.1 o superior)
  - Docker Swarm (iniciado en la máquina)
  - Conexión a Internet para descargar imágenes
- **Conexión LAN:** Para que en el futuro se puedan unir más nodos.

## Arquitectura del Clúster

- **Nodo Manager:**  
  La ASUS TUF actuará como nodo manager. En este entorno de demo, también ejecutará contenedores worker y Jupyter Notebook.
  
- **Contenedores del Clúster:**  
  - **Spark Master:** Coordina la ejecución de trabajos. Se expone en el puerto 7077 (para comunicación con workers) y 8080 (para la interfaz web).
  - **Spark Worker:** Ejecuta las tareas de Spark. Se desplegarán 3 réplicas para la demo.
  - **Jupyter Notebook:** Permite interactuar con el clúster mediante PySpark. Se accede por el puerto 8888.

- **Recursos Compartidos:**  
  - **Red Overlay (spark-net):** Facilita la comunicación entre contenedores.
  - **Volumen (spark-vol):** Se usa para almacenar archivos de datos (por ejemplo, un CSV de 50 GB o 1 TB).

## Pasos de Configuración

### 1. Preparar el Entorno y Limpiar Configuraciones Previas

Si has realizado despliegues anteriores, limpia el entorno. En el nodo manager (tu ASUS TUF), ejecuta:

```bash
# Elimina el stack actual (si existe)
docker stack rm spark-cluster

# Opcional: Limpiar contenedores, redes, volúmenes e imágenes huérfanos
docker container prune -f
docker network prune -f
docker volume prune -f
docker image prune -a -f

# (Opcional) Eliminar contenedores de pruebas
docker rm -f worker1 worker2 worker3
```

### 2. Configurar Docker Swarm en la ASUS TUF (Nodo Manager)

1. **Obtener la IP LAN:**

   ```bash
   ip a
   ```

2. **Iniciar Swarm:**

   ```bash
   docker swarm init --advertise-addr <TU_IP_LAN>
   ```

3. **Obtener el Token para Workers:**

   ```bash
   docker swarm join-token worker
   ```

### 3. Crear Recursos Compartidos: Red Overlay y Volumen

```bash
docker network create --driver overlay spark-net
docker volume create spark-vol
```

### 4. Configurar el Archivo de Despliegue (Stack YAML)

```bash
nano spark-cluster.yml
```

Copia y pega:

```yaml
version: '3.8'

networks:
  spark-net:
    external: true

volumes:
  spark-vol:
    external: true

services:
  spark-master:
    image: bitnami/spark:latest
    networks:
      - spark-net
    ports:
      - "8080:8080"
      - "7077:7077"
    environment:
      - SPARK_MODE=master
    deploy:
      placement:
        constraints:
          - node.role == manager

  spark-worker:
    image: bitnami/spark:latest
    networks:
      - spark-net
    environment:
      - SPARK_MODE=worker
      - SPARK_MASTER_URL=spark://spark-master:7077
      - SPARK_WORKER_CORES=2
      - SPARK_WORKER_MEMORY=4G
    deploy:
      replicas: 3

  jupyter:
    image: jupyter/pyspark-notebook:latest
    networks:
      - spark-net
    ports:
      - "8888:8888"
    environment:
      - JUPYTER_TOKEN=sparkdemo
    volumes:
      - spark-vol:/data
    deploy:
      placement:
        max_replicas_per_node: 1
```

### 5. Desplegar el Stack

```bash
docker stack deploy -c spark-cluster.yml spark-cluster
docker service ls
```

### 6. Probar el Clúster

- **Spark Master UI:** `http://<TU_IP_LAN>:8080`
- **Jupyter Notebook:** `http://<TU_IP_LAN>:8888` (Token: `sparkdemo`)

Ejecuta en Jupyter:

```python
from pyspark.sql import SparkSession

spark = SparkSession.builder     .master("spark://spark-master:7077")     .appName("DemoTest")     .getOrCreate()

rdd = spark.sparkContext.parallelize(range(1, 11))
suma = rdd.sum()
print(f"La suma de 1 a 10 es: {suma}")

spark.stop()
```

## Consideraciones para Escalabilidad

- **Más Workers:** Une nuevas computadoras ejecutando el comando `docker swarm join` obtenido.  
- **Uso de GPU:** Configura etiquetas y usa imágenes con soporte CUDA.

## Conclusión

Este README te permite configurar un clúster funcional y escalable. Con esta base, podrás realizar pruebas con archivos grandes (50 GB o 1 TB) y escalar tu arquitectura añadiendo más nodos.
