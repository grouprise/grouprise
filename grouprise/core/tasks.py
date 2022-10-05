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
