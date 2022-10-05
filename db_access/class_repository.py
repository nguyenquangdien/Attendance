import sqlite3
from db_access.entities import ClassEntity, StudentEntity, AttendanceEntity


class ClassRepository():
    def __init__(self, db_name) -> None:
        self.db_name = db_name
        self.create_table()        

    def create_table(self):
        conn = sqlite3.connect(self.db_name)
        query = '''
            CREATE TABLE IF NOT EXISTS classes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT (20) NOT NULL
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

    def add_class(self, class_entity):
        conn = sqlite3.connect(self.db_name)
        query = '''
            INSERT INTO classes (name) 
            VALUES (?);
            '''
        try:        
            cursor = conn.cursor()
            cursor.execute(query, (class_entity.name,))
            conn.commit()
            print ('insert successfully')
        except:
            print ('error in operation')
            conn.rollback()
        conn.close()

    def get_class(self, id):
        conn = sqlite3.connect(self.db_name)
        query = '''
            SELECT * FROM classes 
            WHERE id = ?;
            '''
        cursor = conn.cursor()
        cursor.execute(query, (id,))
        all_rows = cursor.fetchall()
        class_entities = []
        for row in all_rows:
            class_entities.append(ClassEntity(row[0], row[1]))
        conn.close()
        return class_entities

    def get_all_classes(self):
        conn = sqlite3.connect(self.db_name)
        query = '''
            SELECT * FROM classes;
            '''
        cursor = conn.cursor()
        cursor.execute(query)
        all_rows = cursor.fetchall()
        class_entities = []
        for row in all_rows:
            class_entities.append(ClassEntity(row[0], row[1]))
        conn.close()
        return class_entities

    def delete_class():
        pass

    def update_class():
        pass