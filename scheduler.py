import mysql.connector
import time
from datetime import datetime, timedelta
from dateutil import parser, relativedelta
from database import Database
from apscheduler.schedulers.background import BackgroundScheduler
from mysql.connector import errorcode
class Scheduler:
    def __init__(self):
        # self._db = Database(db_host="localhost", db_user="root", db_password="Shellkode@12345", db_name="geekprofile")
        # Connect to the database
        self.cnx = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Shellkode@12345",
            database="geekprofile"
        )
        self.cursor = self.cnx.cursor()
        self._scheduler = BackgroundScheduler()
        self._scheduler.add_job(self.check_pending, 'interval', minutes=5)
        self._scheduler.start()
    def create_student_table(self):
        try:
            self.cursor.execute("""
                CREATE TABLE students (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255),
                    age INT,
                    scheduled_time DATETIME,
                    status VARCHAR(255), 
                    repeat_interval INT, 
                    repeat_type VARCHAR(255), 
                    repeat_scheduled_time DATETIME

                )
            """)
            self.cnx.commit()
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                print("Table already exists.")
            else:
                print(err.msg)
        else:
            print("Table created successfully.")    
        
    def get_data(self):
        query = "SELECT * FROM student"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return rows


    def insert_data(self, name, age, scheduled_time,repeat_interval, repeat_type,repeat_scheduled_time):
        query = """
            INSERT INTO students (name, age, scheduled_time,repeat_interval, repeat_type,repeat_scheduled_time)
            VALUES (%s, %s, %s,%s,%s,%s)
        """
        values = (name, age, scheduled_time,repeat_interval, repeat_type,repeat_scheduled_time)
        self.cursor.execute(query, values)
        self.cnx.commit()
    def get_pending_data(self):
        query = "SELECT * FROM student WHERE status IN ('scheduled', 'in progress')"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()

        return rows

    def update_status(self, id, status):
        query = "UPDATE student SET status = %s WHERE id = %s"
        values = (status, id)
        self.cursor.execute(query, values)
#interval update
    def check_pending(self):
        rows = self.get_pending_data()
        for row in rows:
            scheduled_time = row[3]
            repeat_interval = row[4]
            repeat_type = row[5]
            repeat_scheduled_time = row[6]
            if repeat_interval is not None and repeat_type is not None and repeat_scheduled_time is not None:
                now = datetime.now()
                if now >= repeat_scheduled_time:
                    name = row[1]
                    age = row[2]
                    self.insert_data(name, age, repeat_scheduled_time, status="scheduled", repeat_interval=repeat_interval, repeat_type=repeat_type, repeat_scheduled_time=None)

                    self.update_status(row[0], "scheduled")
                    print(f"Task for {name} repeated at {now}")
                    continue
            if datetime.now() >= scheduled_time:
                id = row[0]
                name = row[1]
                self.update_status(id, "in progress")
                time.sleep(10) # simulate task being performed
                self.update_status(id, "completed")
                print(f"Status for task with id {id} and name {name} changed to completed at {datetime.now()}")


    def get_repeat_scheduled_time(self, row):
        scheduled_time = row[3]
        repeat_interval = row[5]
        repeat_type = row[6]
        if repeat_type == "daily":
            repeat_scheduled_time = scheduled_time + timedelta(days=repeat_interval)
        elif repeat_type == "weekly":
            repeat_scheduled_time = scheduled_time + timedelta(weeks=repeat_interval)
        elif repeat_type == "monthly":
            repeat_scheduled_time = scheduled_time + relativedelta(months=+repeat_interval)
        elif repeat_type == "years":
            repeat_scheduled_time + relativedelta(years=repeat_interval)
        else:
            repeat_scheduled_time = None
        return repeat_scheduled_time

    def schedule_task(self, name, age, scheduled_time=None):
        scheduled_time = parser.parse(scheduled_time)
        self.insert_data(name, age, scheduled_time, "scheduled")
        if scheduled_time is None:
            scheduled_time = datetime.now() + timedelta(minutes=5)
        else:
            scheduled_time = parser.parse(scheduled_time)

        self.insert_data(name, age, scheduled_time, "scheduled")
        while datetime.now() < scheduled_time:
            time.sleep(1)
        self.update_status(self.get_pending_data()[-1][0], "in progress")
        print(f"Status for {name} changed to in progress at {datetime.now()}")

    def edit_scheduled_time(self, student_id, scheduled_time):
        query = "SELECT scheduled_time, repeat_interval, repeat_type FROM student WHERE id = %s"
        values = (student_id,)
        result = self.cursor.execute(query, values)
        if not result:
            raise ValueError(f"No student found with id {student_id}")
        current_scheduled_time, repeat_interval, repeat_type = result[0]


        # Get current scheduled time and repeat settings
        current_scheduled_time, repeat_interval, repeat_type = result[0]

        # If repeat is set, check if the new scheduled time is valid
        if repeat_interval and repeat_type:
            new_scheduled_time = parser.parse(scheduled_time)
            if new_scheduled_time <= datetime.now():
                raise ValueError("Scheduled time must be in the future")
            if repeat_type == "daily":
                if (new_scheduled_time - datetime.now()).days % (7 * repeat_interval) != 0:

                    raise ValueError(f"Scheduled time must be {repeat_interval} days apart for daily repeat")
            elif repeat_type == "weekly":
                if (new_scheduled_time - datetime.now()).days % (7 * repeat_interval) != 0:
                    raise ValueError(f"Scheduled time must be {repeat_interval} weeks apart for weekly repeat")

        # Update the scheduled time
        query = "UPDATE student SET scheduled_time = %s WHERE id = %s"
        values = (scheduled_time, student_id)
        self.cursor.execute(query, values)

        # If the student is currently in progress, reset status to scheduled
        if current_scheduled_time <= datetime.now():
            query = "UPDATE student SET status = 'scheduled' WHERE id = %s"
            values = (student_id,)
            self.cursor.execute(query, values)

        

    def schedule_repeat_task(self, name, age, repeat_interval, repeat_type,repeat_scheduled_time ):
        scheduled_time = datetime.now()
        self.insert_data(name, age, scheduled_time, "scheduled", repeat_interval, repeat_type, repeat_scheduled_time)
        while True:
            self.check_pending()
            time.sleep(1)
    
    def delete_task(self,id):
        schedule_id = input("Enter the id of the schedule to delete: ")
        # schedule_id = id
        try:
            schedule = self.get_pending_data(schedule_id)
            if not schedule:
                print(f"Schedule with id {schedule_id} does not exist.")
                return
            confirm = input(f"Are you sure you want to delete schedule with id {schedule_id}? (y/n) ")
            if confirm.lower() == 'y':
                self.delete_schedule(schedule_id)
                print(f"Schedule with id {schedule_id} deleted successfully.")
            else:
                print(f"Schedule with id {schedule_id} not deleted.")
        except Exception as e:
            print("Error deleting schedule:", e)
        
    def delete_schedule(self):
        id = input("Enter id: ")
        query = "DELETE FROM student WHERE id = %s"
        values = (id)
        self.cursor.execute(query, values)
        self.cnx.commit()