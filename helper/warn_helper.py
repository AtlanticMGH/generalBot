import mysql.connector
import dotenv
import os
from typing import cast

dotenv.load_dotenv()

mydb = mysql.connector.pooling.MySQLConnectionPool(
    pool_name="warnPool",
    pool_size=10,
    connection_timeout=5,
    host=os.getenv("DB-SERVER"),
    user=os.getenv("DB-USER"),
    password=os.getenv("DB-PASSWORD"),
    database=os.getenv("DB-NAME"),

    raise_on_warnings=True,
    pool_reset_session=True
)

class Warn_helper():
    def calculateTimeoutLength(self, user_id, guild_id):
        with mydb.get_connection() as conn:
            with conn.cursor() as mycursor:
                if not self.checkIfTableExists(guild_id, mycursor):
                    target_table = f"{guild_id}_warns"
                    sql = (f"CREATE TABLE `{target_table}` (user_id varchar(32), warns int, timeouts int)")
                    mycursor.execute(sql)
                    conn.commit()

                target_table = f"{guild_id}_warns"
                try:
                    sql = f"SELECT timeouts from {target_table} where user_id = (%s)"
                    val = (user_id,)
                    mycursor.execute(sql, val)
                    timeouts = mycursor.fetchall()
                except Exception as e:
                    print(f"Fehler beim berechnen der Länge: {e}")
                    return -1

                if not timeouts: # Falls User nicht existiert
                    return 1
                return 2**timeouts[0][0]

    def checkIfTableExists(self, table_name2, mycursor) -> bool:
        target_table = f"{table_name2}_warns"
        sql = ("SELECT * FROM information_schema.tables WHERE table_name = %s")
        val = (target_table,)
        mycursor.execute(sql, val)
        result = mycursor.fetchall()
        if result:
            return True
        return False

    def read_warns(self, user_id, guild_id):
        conn = None
        try:
            conn = mydb.get_connection()
            # buffered=True ist hier der Retter
            with conn.cursor(buffered=True) as mycursor:
                # Prüfen
                target_table = f"{guild_id}_warns"
                mycursor.execute("SHOW TABLES LIKE %s", (target_table,))
                if not mycursor.fetchone():
                    mycursor.execute(f"CREATE TABLE `{target_table}` (user_id varchar(32), warns int, timeouts int)")
                    conn.commit()

                # Auslesen
                sql = f"SELECT warns FROM `{target_table}` WHERE user_id = %s"
                mycursor.execute(sql, (user_id,))
                result = mycursor.fetchall()
                return [row[0] for row in result]
        except Exception as e:
            print(f"DB Fehler: {e}")
            return []
        finally:
            if conn and conn.is_connected():
                conn.close() # Manuelle Rückgabe zur Sicherheit

    def add_warn(self, user_id, guild_id):
        with mydb.get_connection() as conn:
            with conn.cursor() as mycursor:
                target_table = f"{guild_id}_warns"
                if not self.checkIfTableExists(guild_id, mycursor):
                    sql = (f"CREATE TABLE `{target_table}` (user_id varchar(32), warns int, timeouts int)")
                    mycursor.execute(sql)
                    conn.commit()

                warns = []
                try:
                    sql = f"SELECT warns from {target_table} where user_id = (%s)"
                    val = (user_id,)
                    mycursor.execute(sql, val)
                    warns = mycursor.fetchall()
                except Exception as e:
                    print(f"Fehler beim auslesen von warns: {e}")

                if warns:
                    sql = f"UPDATE {target_table} SET `warns` = (%s) WHERE user_id = (%s)"
                    val = (warns[0][0]+1, user_id,)
                else:
                    sql = f"INSERT INTO {target_table} (user_id, warns, timeouts) VALUES (%s, 1, 0)"
                    val = (user_id,)

                mycursor.execute(sql, val)
                conn.commit()
                print("geschlossen (automatisch via with)")

    def reset_warns(self, guild_id, user_id):
        with mydb.get_connection() as conn:
            with conn.cursor() as mycursor:
                if not self.checkIfTableExists(guild_id, mycursor):
                    target_table = f"{guild_id}_warns"
                    sql = (f"CREATE TABLE `{target_table}` (user_id varchar(32), warns int, timeouts int)")
                    mycursor.execute(sql)
                    conn.commit()

                target_table = f"{guild_id}_warns"
                try:
                    sql = f"SELECT timeouts from {target_table} where user_id = (%s)"
                    val = (user_id,)
                    mycursor.execute(sql, val)
                    timeouts = mycursor.fetchall()
                except Exception as e:
                    print(f"Fehler beim reseten von warnungen: {e}")
                    return True

                if timeouts:
                    if timeouts[0][0]>=9:
                        return False
                    sql = f"UPDATE {target_table} SET `warns` = 0, `timeouts` = %s WHERE user_id = (%s)"
                    val = (timeouts[0][0]+1, user_id,)
                    mycursor.execute(sql, val)
                    conn.commit()
                    return True

    def delete_warn(self, guild_id, user_id):
        with mydb.get_connection() as conn:
            with conn.cursor() as mycursor:
                if not self.checkIfTableExists(guild_id, mycursor):
                    target_table = f"{guild_id}_warns"
                    sql = (f"CREATE TABLE `{target_table}` (user_id varchar(32), warns int, timeouts int)")
                    mycursor.execute(sql)
                    conn.commit()

                sql = f"DELETE FROM {guild_id}_warns WHERE user_id = %s"
                val = (user_id,)
                mycursor.execute(sql, val)
                conn.commit()
