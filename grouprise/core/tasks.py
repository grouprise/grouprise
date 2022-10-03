from django.conf import settings
from django.utils.module_loading import import_string
from huey.contrib.djhuey import db_task

from grouprise.core.models import RepeatableTask


class TaskPriority:
    """numeric values to be used by `huey` for prioritizing tasks

    Higher values take precedence over lower values.
    Huey's default priority is zero.
    We use a negative range for custom priorities.
    Thus all tasks without a specific priority are scheduled with the highest priority by default.
    """

    NOTIFICATION = 0
    STATISTICS = -10
    SYNCHRONIZATION = -5


class TaskExpiry:
    """discard tasks, which are not started within a given maximum delay

    We need to prevent tasks from piling up.
    Thus we discard tasks, if they are delayed by more than half of their scheduling period.
    """

    HOURLY = 1800


@db_task()
def auto_task(obj):
    """Store an object-related task temporarily in the database, execute it and remove the db entry

    The task is removed from the database after execution, if it finished successfully.
    In case of failure, the task remains in the database and thus can be re-attempted manually
    (via `grouprisectl repeat_tasks`).

    The task (function) to be executed depends on the model of the given object.
    The mapping from object/model to function is configured in GROUPRISE_REPEATABLE_TASKS.
    """
    # store the task temporarily - it will be removed below in case of success
    task = RepeatableTask.objects.create(
        content_type=obj.content_type, object_id=obj.id
    )

    # retrieve the function configured for this object type
    obj_class_label = obj._meta.label
    func_name = settings.GROUPRISE_REPEATABLE_TASKS[obj_class_label]
    func = import_string(func_name)
    # The execution of the taskmay fail.  Problems are handled by our caller.
    func(obj)
    # The task finished successfully, thus we can remove it from the database.
    task.delete()
