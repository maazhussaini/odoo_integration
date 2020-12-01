import mysql.connector as sql

conn = sql.connect(host="localhost", user="root", password="", database="android")
cursor = conn.cursor()
sql_que = "select * from users"

cursor.execute(sql_que)

records = cursor.fetchall()
print("No. of Users", cursor.rowcount)


for rec in records:
    print("ID", rec[0])
    print("Name: ", rec[1])
    print("PWD: ", rec[2])
    print("Email: ", rec[3])


cursor.close()
conn.close()