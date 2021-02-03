import pyodbc
from xmlrpc import client as xmlrpclib
from datetime import date
import datetime


conn = pyodbc.connect(r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=E:\Taza\ATT2000.MDB;')
cursor = conn.cursor()


sql = "SELECT T1.USERID, MAX(Select MIN(DATEADD('h',-5,T2.CHECKTIME)) FROM CHECKEXACT T2 WHERE T2.CHECKTYPE = 'I' and " 
sql += "T2.USERID = T1.USERID and Format(CDate(T2.Date),'dd-mm-yyyy')=Format(CDate(T1.Date),'dd-mm-yyyy')) "
sql += "AS CheckIn, MAX(Select MAX(DATEADD('h',-5,T3.CHECKTIME)) FROM CHECKEXACT T3 WHERE T3.CHECKTYPE = 'O' and " 
sql += "T3.USERID = T1.USERID and Format(CDate(T3.Date),'dd-mm-yyyy')=Format(CDate(T1.Date),'dd-mm-yyyy')) AS " 
sql += "CheckOut, Format(CDate(Date),'dd-mm-yyyy') AS CreateDate FROM CHECKEXACT T1 WHERE Format(CDate(T1.Date),'dd-mm-yyyy') = " 
sql += "Format(CDate(DATE()),'dd-mm-yyyy') GROUP BY T1.USERID, Format(CDate(T1.Date),'dd-mm-yyyy')"

cursor.execute(sql)
# ("SELECT T1.USERID, MAX(Select MIN(DATEADD('h',-5,T2.CHECKTIME)) FROM CHECKEXACT T2 WHERE T2.CHECKTYPE = 'I' and T2.USERID = T1.USERID and Format(CDate(T2.Date),'dd-mm-yyyy')=Format(CDate(T1.Date),'dd-mm-yyyy')) AS CheckIn, MAX(Select MAX(DATEADD('h',-5,T3.CHECKTIME)) FROM CHECKEXACT T3 WHERE T3.CHECKTYPE = 'O' and T3.USERID = T1.USERID and Format(CDate(T3.Date),'dd-mm-yyyy')=Format(CDate(T1.Date),'dd-mm-yyyy')) AS CheckOut, Format(CDate(Date),'dd-mm-yyyy') AS CreateDate FROM CHECKEXACT T1 WEHRE T1.DATE = DATE() GROUP BY T1.USERID, Format(CDate(T1.Date),'dd-mm-yyyy')")

records = cursor.fetchall()

# ODOO DATABASE CONNECTION ##

url = 'http://localhost:8069'
db = 'demo1'
username = 'admin'
password = 'admin'

    ##  ODOO    ##
common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(url))
models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(url))
uid = common.login(db, username, password)

for i in records:
    print(str(i[1]), str(i[2]))
    if i[1] and i[2]:
        id = models.execute_kw(db, uid, password, 'hr.attendance', 'create', [{
            'employee_id': i[0], 'check_in': str(i[1]), 'check_out': str(i[2])
        }])

        print(id)