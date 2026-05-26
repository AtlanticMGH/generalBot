import mysql.connector
import dotenv
import os
from typing import cast

dotenv.load_dotenv()

mydb = mysql.connector.pooling.MySQLConnectionPool(
    pool_name = "bannedWordsPool",
    pool_size=5,
    host=os.getenv("DB-SERVER"),
    user=os.getenv("DB-USER"),
    password=os.getenv("DB-PASSWORD"),
    database=os.getenv("DB-NAME")
)

class Sql_helper():
    def checkIfTableExists(self, table_name2):
        conn = mydb.get_connection()
        mycursor = conn.cursor()
        target_table = f"{table_name2}_banned_words"
        sql = ("SELECT * FROM information_schema.tables WHERE table_name = %s")
        val = (target_table,)
        mycursor.execute(sql, val)
        result = mycursor.fetchall()
        if result:
            return
        sql = (f"CREATE TABLE `{target_table}` (word varchar(128))")
        mycursor.execute(sql)
        conn.commit()

        mycursor.close()
        conn.close()

    def read_banned_words(self, guild_id):
        conn = mydb.get_connection()
        mycursor = conn.cursor()
        self.checkIfTableExists(guild_id)
        target_table = f"{guild_id}_banned_words"
        sql = (f"SELECT * FROM {target_table}")
        mycursor.execute(sql)
        result = cast(list[tuple], mycursor.fetchall())

        mycursor.close()
        conn.close()
        return [row[0] for row in result] # row ist ein tupel

    def add_banned_word(self, word, guild_id):
        conn = mydb.get_connection()
        mycursor = conn.cursor()
        self.checkIfTableExists(guild_id)
        sql = f"INSERT INTO {guild_id}_banned_words (word) VALUES (%s)"
        val = (word,)
        mycursor.execute(sql, val)
        conn.commit()

        mycursor.close()
        conn.close()

    def delete_banned_word(self, word, guild_id):
        conn = mydb.get_connection()
        mycursor = conn.cursor()
        self.checkIfTableExists(guild_id)
        sql = f"DELETE FROM {guild_id}_banned_words WHERE word = %s"
        val = (word,)
        mycursor.execute(sql, val)
        comm.commit()
        mycursor.close()
        conn.close()
