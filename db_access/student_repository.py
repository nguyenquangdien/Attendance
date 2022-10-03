import sqlite3
from db_access.entities import ClassEntity, StudentEntity, AttendanceEntity


class StudentRepository():
    def __init__(self, db_name) -> None:
        self.db_name = db_name
        self.create_table()        

    def create_table(self):
        conn = sqlite3.connect(self.db_name)
        query = '''
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT (100) NOT NULL,
                student_id TEXT (100) NOT NULL UNIQUE,
                birthday TEXT,
                class_id INTEGER NOT NULL,
                encode_data_path TEXT (500),
                FOREIGN KEY(class_id) REFERENCES classes(id)  
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

    def add_student(self, student_entity):
        conn = sqlite3.connect(self.db_name)
        query = '''
            INSERT INTO students (name, student_id, birthday, class_id, encode_data_path) 
            VALUES (?,?,?,?,?);
            '''
        try:        
            cursor = conn.cursor()
            cursor.execute(query, (student_entity.name,student_entity.student_id, student_entity.birthday, student_entity.class_id, student_entity.encode_data_path))
            conn.commit()
            print ('insert successfully')
        except:
            print ('error in operation')
            conn.rollback()
        conn.close()

    def get_by_student_id(self, student_id):
        conn = sqlite3.connect(self.db_name)
        query = '''
            SELECT * FROM students 
            WHERE id = {};
            '''
        cursor = conn.cursor()
        query.format(student_id)
        cursor.execute(query)
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