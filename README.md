# django-datajsonar

## Configuración

### Scheduling de trabajos

Los comandos `schedule_indexation` y `schedule_task_finisher` permiten planificar trabajos que se ejecutarán de manera
periódica. Es posible definir un horario de inicio, un intervalo de tiempo entre corridas y la función a ejecutar. Los
parámetros son idénticos para los dos comandos.

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
  `schedule_indexation` es `django_datajsonar.libs.indexing.tasks.schedule_new_read_datajson_task`; para
  `schedule_task_finisher` es `django_datajsonar.libs.indexing.tasks.close_read_datajson_task`.

En caso de querer registrar un trabajo con callable e intervalo iguales a un trabajo ya registrado, se notificará la
situación y se preservará el trabajo original sin guardar el nuevo.