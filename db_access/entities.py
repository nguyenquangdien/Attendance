from dataclasses import dataclass
 
@dataclass
class ClassEntity(): 
    id: int
    name: str


@dataclass
class StudentEntity(): 
    id: int
    name: str
    birthday: str
    student_id: str
    class_id: int
    encode_data_path: str

@dataclass
class AttendanceEntity(): 
    id: int
    day: str
    student_id: str
    enter_time: str
    exit_time: str  