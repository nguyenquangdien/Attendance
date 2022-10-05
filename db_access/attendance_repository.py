import sqlite3
from db_access.entities import ClassEntity, StudentEntity, AttendanceEntity


class AttendanceRepository():
    def __init__(self, db_name) -> None:
        self.db_name = db_name
        self.create_table()        

    def create_table(self):
        conn = sqlite3.connect(self.db_name)
        query = '''
            CREATE TABLE IF NOT EXISTS attendances (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                day TEXT NOT NULL,
                student_id TEXT (100) NOT NULL,
                enter_time TEXT,
                exit_time TEXT,
                FOREIGN KEY(student_id) REFERENCES students(student_id)    
            );
            '''
        try:        
            cursor = conn.cursor()
            cursor.execute(query)
            print ('table created successfully')
        except:
            print ('error in operation')
            conn.rollback()
        conn.close()

    def add_attendance(self, attendance_entity):
        conn = sqlite3.connect(self.db_name)
        query = '''
            INSERT INTO attendances (day, student_id, enter_time) 
            VALUES (?,?,?);
            '''
        try:        
            cursor = conn.cursor()
            cursor.execute(query, (attendance_entity.day,attendance_entity.student_id, attendance_entity.enter_time))
            conn.commit()
            print ('insert successfully')
        except:
            print ('error in operation')
            conn.rollback()
        conn.close()

    def get_by_day(self, student_id):
        conn = sqlite3.connect(self.db_name)
        query = '''
            SELECT * FROM attendances 
            WHERE id = ?;
            '''
        cursor = conn.cursor()
        cursor.execute(query, (student_id))
        all_rows = cursor.fetchall()
        student_entities = []
        for row in all_rows:
            student_entities.append(StudentEntity(row[0], row[1], row[2], row[3], row[4], row[5]))
        conn.close()
        return student_entities

    def get_all_students(self):
        conn = sqlite3.connect(self.db_name)
        query = '''
            SELECT * FROM students;
            '''
        cursor = conn.cursor()
        cursor.execute(query)
        all_rows = cursor.fetchall()
        student_entities = []
        for row in all_rows:
            student_entities.append(StudentEntity(row[0], row[1], row[2], row[3], row[4], row[5]))
        conn.close()
        return student_entities

    def delete_student():
        pass

    def update_student():
        pass