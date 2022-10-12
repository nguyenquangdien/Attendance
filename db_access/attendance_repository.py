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

    def check_student_attendance(self, student_id, day):
        conn = sqlite3.connect(self.db_name)
        query = '''
            SELECT COUNT(*) AS num_attendance
            FROM attendances
            WHERE attendances.student_id = ? AND attendances.day = ?;
            '''
        cursor = conn.cursor()
        cursor.execute(query, (student_id, day))
        query_result = cursor.fetchall()
        conn.close()
        return (int)(query_result[0][0]) > 0