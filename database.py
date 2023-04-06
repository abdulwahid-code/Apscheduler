import mysql.connector

class Database:
    def __init__(self, db_host, db_user, db_password, db_name):
        self._cnx = mysql.connector.connect(
            host=db_host, 
            user=db_user,
            password=db_password,
            database=db_name
        )
        self._cursor = self._cnx.cursor()        
    def execute(self, query, values=None):
        if values:
            self._cursor.execute(query, values)
        else:
            self._cursor.execute(query)
        self._cnx.commit()

db_host = "localhost"
db_user = "root"
db_password = "Shellkode@12345"
db_name = "geekprofile"
database = Database(db_host, db_user, db_password, db_name)
