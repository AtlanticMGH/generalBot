import mysql.connector
import dotenv
import os
from typing import cast

dotenv.load_dotenv()

mydb = mysql.connector.pooling.MySQLConnectionPool(
    pool_name = "modLogsPool",
    pool_size=5,
    host=os.getenv("DB-SERVER"),
    user=os.getenv("DB-USER"),
    password=os.getenv("DB-PASSWORD"),
    database=os.getenv("DB-NAME")
)
table = "modLogs"

# db schema: user_id; log; action_title; date

class ModLogs():
    def checkIfTableExists(self, table_name):
        conn = mydb.get_connection()
        mycursor = conn.cursor()
        
        sql = (f"SELECT * FROM information_schema.tables WHERE table_name = {table_name} LIMIT 1;")
        mycursor.execute(sql)
        result = mycursor.fetchall()
        if result:
            return
        sql = (f"CREATE TABLE `{table_name}` (user_id varchar(32), log text(65535), action_title varchar(32), date date);")
        mycursor.execute(sql)
        conn.commit()
 
        mycursor.close()
        conn.close()
       

    #WICHTIG:
    #Zum table guild id hinzufügen, sodass auf einem 2. server nicht auf die logs von einem anderen
    #server zugreifen kann
    def log_hinzufuegen(self, guild_id, user_id, log, action_title, date): # bei log, nur grund/beschreibung
        conn = mydb.get_connection()
        mycursor = conn.cursor()
        self.checkIfTableExists(guild_id)
        sql = (f"INSERT INTO `{guild_id}` (user_id, log, action_title, date) VALUES (%s, %s, %s, %s)")
        val = (str(user_id), log, action_title, date)
        mycursor.execute(sql, val)
        conn.commit()

        mycursor.close()
        conn.close()
 
    def logs_lesen(self, guild_id, user_id):
        conn = mydb.get_connection()
        mycursor = conn.cursor()
        self.checkIfTableExists(guild_id)
        sql = (f"SELECT log, action_title, date FROM `{guild_id}` WHERE user_id = (%s)")
        val = (user_id,)
        mycursor.execute(sql, val)
        result = cast(list[tuple], mycursor.fetchall())
 
        mycursor.close()
        conn.close()
        return [row for row in result]

