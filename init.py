import sqlite3

conn = sqlite3.connect("corona.db")
cursor = conn.cursor()

cursor.execute("""CREATE TABLE corona
                  (title text, amount integer DEFAULT 0)
               """)
