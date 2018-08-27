## Uso


### Carga de Nodos

Despues de iniciar sesion como Administrador, debemos cargar un nuevo `Node Register file`.
Esta pagina se encuentra en la ruta `/admin/django_datajsonar/noderegisterfile/`.
Este archivo tiene un registro de los nodos _a federar_. Ese un archivo de extencion `.yml` y
tiene un aspecto como el siguiente:


```yaml
datosgobar:
  url: "http://datos.gob.ar/data.json"
  formato: "json"
  federado: false

transporte-bis:
  url: "http://datos.transporte.gob.ar/data.json"
  formato: "json"
  federado: false

# Mas nodos...
```

Luego de que creamos la nueva instancia, volvemos a la pagina del listado y deberiamos ver algo como
la siguiente imagen:

![Node register file list](images/node_register_file.png)

Luego seleccionamos la instancia y usamos la accion "Process node file", como se muestra en la imagen:

![Process Node register file list](images/process_node_register_file.png)

Eso procesara el archivo (puede tardar un poco), y al terminar veremos los nodos detectados en
`/admin/django_datajsonar/node/`, algo parecido a

![Nodes list](images/nodes_list.png)


### Lectura de catalogos

Para lanzar una lectura de todos los catalogos de los nodos, podemos instancia una `ReadDataJsonTask`.
Para eso nos dirigimos a la ruta `/admin/django_datajsonar/readdatajsontask/`.
Esta instancia no requiere ningun parametro, ya que leera los datos necesarios de las instancias `Node`
del proceso anterior.
Esta instancia ira registrando los "logs" y "resultados" del proceso. Podremos ver algo como:

![Read DataJson Task](images/read_datajson_task.png)

### Cierre de la tarea

Por una cuestion de concurrencia, las tareas no quedaran en estado "Finalizada" por si solas.
Para que el sistema verifique es estado de las tareas, debemos instanciar un `RepeatableJob`.
Para eso vamos a la ruta `/admin/scheduler/repeatablejob/`.

En el campo **nombre** podemos poner lo que deseemos (como ""), en el campo **callable** debemos
poner `django_datajsonar.indexing.tasks.close_read_datajson_task`.
En el campo **Queue** ponemos `indexing`.
En los campos **fecha** y **hora** de **scheduled time** hacemos click en "Hoy" y "Ahora".
Finalmente en **interval** ponemos `10` y en **interval unit** `minutes`.
Luego de guardar la instancia deberiamos tener algo como:

![Close Read DataJson Task]()
![Close Read DataJson Task](images/close_read_datajson_task.png)


### Lectura periodica

Para que la lectura de los catalogos se ejecute periodicamente, debemos crear un `RepeatableJob`.

Para eso vamos a la ruta `/admin/scheduler/repeatablejob/`.

En el campo **nombre** podemos poner lo que deseemos (como "New Read Datajson Task"), en el campo **callable** debemos
poner `django_datajsonar.tasks.schedule_new_read_datajson_task`.
En el campo **Queue** ponemos `indexing`.
Habilitar el campo **Enabled**.
En los campos **fecha** y **hora** de **scheduled time** hacemos click en "Hoy" y "Ahora".
Finalmente en **interval** ponemos `1` y en **interval unit** `days`.
Luego de guardar la instancia deberiamos tener algo como:

![New Read DataJson Task](images/new_read_datajson_task.png)

Una alternativa a este método es usar un management command. Los comandos `schedule_indexation` y
`schedule_task_finisher` permiten planificar trabajos que se ejecutarán de manera periódica. Es posible definir un
horario de inicio, un intervalo de tiempo entre corridas y la función a ejecutar. Los parámetros son idénticos para los
dos comandos.

Por default, `schedule_indexation` ejecuta periódicamente `schedule_new_read_datajson_task`. Esta función crea nuevas
tareas que iteran sobre los nodos indexables de la red de catálogos y sobre sus datasets creando o actualizando su
metadata en los modelos dependiendo del caso que corresponda. En el caso de `schedule_task_finisher`, por default corre
`close_read_datajson_task`. Esta función marca como finalizadas los `ReadDataJsonTask` una vez que terminan para poder
crear nuevas tareas. En conjunto, estos trabajos permiten crear, poblar y actualizar los modelos indexables de manera
periódica y automática.

Para ejecutar el comando hay que llamar:

`$ python manage.py [schedule_indexation|schedule_task_finisher] NAME -t HOUR MINUTE -i UNIT [weeks|days|hours|minutes] -c CALLABLE`

Los comandos toman los siguientes parámetros:
  - **Name**: Es el nombre con que queda registrado el trabajo. Si el nombre pertenece a un trabajo ya registrado, se
  procederá a actualizarlo con los valores pasados.
  - **Time**: La hora de inicio del trabajo, efectivo al día siguiente. Por default en `schedule_indexation` son las 6
  de la mañana (hora UTC); para `schedule_task_finisher` es la medianoche (UTC).
  - **Interval**: El intervalo de tiempo que se deja entre corrida y corrida. Por default en `schedule_indexation` es
  24 horas; para `schedule_task_finisher` son 5 minutos.
  - **Callable**: La función que se ejecutará en los horarios e intervalos definidos. Por default en
  `schedule_indexation` es `django_datajsonar.tasks.schedule_new_read_datajson_task`; para
  `schedule_task_finisher` es `django_datajsonar.indexing.tasks.close_read_datajson_task`.

En caso de querer registrar un trabajo con callable e intervalo iguales a un trabajo ya registrado, se notificará la
situación y se preservará el trabajo original sin guardar el nuevo.

### Configuración de datasets indexables

Hay 2 formas de marcar un nodo como indexable, manualmente o cargando un csv de configuración. Para el caso manual, se
puede marcar en el modelo o, marcar un subconjunto de los datasets y ejecutar la acción "Marcar como indexable".

El otro método es cargando un nuevo `Dataset Indexing file`.
Esta pagina se encuentra en la ruta `/admin/django_datajsonar/datasetindexingfile/`.
Este archivo tiene un registro de los datasets _indexables_. Ese un archivo de extencion `.csv` y
tiene un aspecto como el siguiente:


```
catalog_id,dataset_identifier
sspm,399
sspm,330
enacom,REGIS-DE-PROVE-POSTA
acumar,cb351aa5-731b-458b-8227-a0c5b828356f
# Más entradas
```

La primera columna tiene el identificador del catalogo, y la segunda el identificador del dataset que se desea marcar
como indexable.

Luego de que creamos la nueva instancia, volvemos a la pagina del listado y deberiamos ver algo como
la siguiente imagen:

![Node register file list](images/dataset_indexing_file.png)

Luego seleccionamos la instancia y usamos la accion "Process node file", como se muestra en la imagen:

![Process Node register file list](images/process_indexing_file.png)

Eso procesa el archivo (puede tardar un poco), y al terminar veremos los datasets marcados como indexables en
`/admin/django_datajsonar/node/`.

### Definición de tareas default

Es posible definir tareas default en los settings de la aplicación. En el archivo de settings definir la lista:

```
DEFAULT_TASKS = [

    ...

    {
        'name': <nombre>,
        'callable': <callable del metodo a ejecutar>,
        'start_hour': <hora de inicio>,
        'start_minute': <minuto de inicio>,
        'interval': <intervalo con el cual se repite el job>,
        'interval_unit': <minutes|hours|days|weeks>,
    },
    
    ...
}
``` 

Cada diccionario define una tarea a ser programada por `django-rq-scheduling`. Llamar al comando 
`python manage.py schedule_default_tasks` crea los repeatable jobs ahí definidos. (Nota: en caso de 
tener una tarea con un nombre ya definido en los defaults, llamar el comando actualizará esta tarea
con los valores definidos en `DEFAULT_TASKS`)
