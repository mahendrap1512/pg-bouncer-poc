from enum import Enum

class TaskStatus(int, Enum):
    PLANNED = 0
    TODO = 1
    IN_PROGRESS = 2
    COMPLETED = 3