from dataclasses import dataclass
from enum import Enum


class EnterStatus(Enum):
    ON_TIME = 0
    LATE = 1
    NOT_ENTER = 2


@dataclass
class AttendanceInfo(): 
    student_id: str
    student_name: str
    class_name: str
    enter_time: str
    status: EnterStatus
