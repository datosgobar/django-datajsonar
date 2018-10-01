## Sincronización en etapas de tareas

### Synchronizer

*Class Synchronizer()*

La clase `Synchronizer` maneja el proceso general de las distintas tareas que se ejecutan.
Guarda en `start_stage` donde comienza el proceso y en `actual_stage` la etapa que se está
ejecutando en el momento. Además está identificado por el campo `name` y un estado `status`
que marca si hay alguna tarea corriendo

*begin_stage(self, stage=None)*

El método indica al synchronizer que debe empezar la etapa pasada por parámetro. Si `stage`
es `None`, el synchronizer arranca con la etapa inicial.

*check_completion(self)*

Este método chequea el estado del stage actual. En caso de que haya terminado, cierra la
tarea actual (en caso que aplique) y comienza la siguiente etapa. Si la etapa terminada era
la última, pone el synchronizer en stand-by

### Stage

*Class Stage()*

La clase `Stage` maneja la ejecución de una tarea en particular. Tiene un `status` que marca
si la etapa está corriendo o inactiva. El método que corre se define en `callable_str`, este
campo debe ser el nombre calificado de un callable. El campo `queue` marca la cola de Redis
que debe chequear el stage para ver si el método definido en `callable_str` terminó.
Opcionalmente, se puede pasar el nombre calificado de un task que herede de `AbstractTask`;
en ese caso el stage cierra la tarea abierta una vez que termina. Finalmente, `next_stage`
guarda la siguiente etapa dentro del proceso.

*close_task_if_finished(self)*

Chequea el estado de la cola definida en `queue`, Devuelve `True` en caso de que no haya jobs
pendientes, `False` en caso contrario. Adicionalmente, si la tarea terminó y tiene definido un
`task`, cierra el task abierto.

*get_running_task(self)*

Devuelve la última tarea creada con estado `RUNNING` del modelo definido en `task`. Si el campo
no está definido o, no hay una tarea corriendo, devuelve `None`

## Uso

Primero es necesario crear y guardar cada etapa armando con ellas la secuencia a seguir. Luego,
crear el sincronizador apuntando a la etapa inicial. El proceso arranca cuando el sincronizador
ejecuta `begin_stage()` y va avanzando mediante llamadas de `check_completion()`. Para lograr
esto, es posible programar 2 repeatable jobs con los callables : `django_datajsonar.synchronizer_tasks.start_synchros`
y `django_datajsonar.synchronizer_tasks.start_synchros` para hacer estas llamadas periódicas.

 