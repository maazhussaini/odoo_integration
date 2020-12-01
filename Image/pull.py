##      LIBERIES       ##

from xmlrpc import client as xmlrpclib
import mysql.connector as sql
from operator import itemgetter

        ## ODOO DATABASE CONNECTION ##

url = 'http://192.168.18.99:8069'
db = 'abs_odoo'
username = 'skr2570@gmail.com'
password = 'abs_admin'

        ## MYSQL DATABASE CONNECTION ##

# conn = sql.connect(host="localhost", user="root", password="", database="odoo_dummy")
# cursor = conn.cursor()

        ## CONNECTION END

        ## ODOO 

common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(url))
models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(url))

uid = common.login(db, username, password)

var = common.version()

models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(url))

        ## PULL FROM ODOO
# records = models.execute_kw(db, uid, password,
#     'sale.order', 'search_read',
#     [[]],
#     {'fields': ['id', 'campaign_id', 'source_id', 'medium_id', 'name', 'state', 'date_order', 
#     'require_signature', 'require_payment', 'user_id', 'partner_id', 'partner_invoice_id', 'partner_shipping_id', 'pricelist_id',
#     'invoice_status', 'amount_untaxed', 'amount_tax', 'amount_total', 'currency_rate', 
#     'company_id', 'team_id', 'create_uid', 'write_uid', 'picking_policy', 'warehouse_id'
#     ]})

records_list = models.execute_kw(db, uid, password,
    'sale.order', 'search_read',
    [[]],
    {'fields': ['campaign_id', 'source_id'], 'limit':2 })

records = models.execute_kw(db, uid, password,
    'sale.order', 'search_read',
    [[]],
    {'fields': ['name', 'state'], 'limit':2 })

combo = []

for i in range(len(records)):
        combo.append([])
        for key, val in records[i].items():
                if key != "id":
                        combo[i].append(val)

rec_list=  []

for i in range(len(records_list)-1):
        for a, b in records_list[i].items():
                if a != 'id':
                        rec_list.append(b)
        


print(combo)
print(rec_list)

final= []
leng = len(combo)
for i in range(leng):
        for j in range(len(combo)):
                combo[i].append(rec_list[j][1])

print(combo)
# try:
#         query = "INSERT INTO sale_order (name, state, campaign_id, source_id) VALUES (%s, %s, %s, %s)"
#         cursor.executemany(query,combo)
#         print("Row inserted",cursor.lastrowid)
# except Exception as err:
#         print("Error:", err)
#         # print(name_list[0])
# else:
#         print("Inserted")
#         conn.commit()
# finally:
#         cursor.close()
#         conn.close