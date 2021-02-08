from xmlrpc import client as xmlrpclib
import mysql.connector as sql
from datetime import date

        ## ODOO DATABASE CONNECTION ##

url = 'http://localhost:8069'
db = 'anfords_odoo'
username = 'admin'
password = 'admin'

        ## ODOO DATABASE CONNECTION END ##

        ## ODOO ##

common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(url))
models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(url))

uid = common.login(db, username, password)

var = common.version()

models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(url))


today_date = str(date.today())

stock_picking_id = models.execute_kw(db, uid, password, 'stock.picking', 'search', 
                                [[['x_api_date', '=', today_date]]])

print(stock_picking_id)
stock_picking_move_id = []
stock_prod_id_rec_list= []

# for i in range(len(stock_picking_id)):
#         stock_picking_move_id.append(models.execute_kw(db, uid, password, 'stock.move', 'search_read', 
#                                 [[['picking_id', '=', stock_picking_id[i]]]], {'fields':['reference', 'origin', 'product_uom_qty']}))

stock_picking_move_id.append(models.execute_kw(db, uid, password, 'stock.move', 'search_read', 
                        [[['picking_id', '=', stock_picking_id]], {'fields':['reference', 'origin', 'product_uom_qty']}]))

print(stock_picking_move_id)

# for j in range(len(stock_picking_move_id)):
#         stock_prod_id_rec_list.append([])
#         for a, b in stock_picking_move_id[j].items():
#                 if a != 'id':
#                         stock_prod_id_rec_list[j].append(b)
                                
# for i in range(len(stock_picking_move_id)):
#         if stock_picking_move_id[i] != "":
#                 for j in stock_picking_move_id[i]:
#                         print(j)
#                 print("\n")
#                 # stock_prod_id_rec_list.append([])
#                 # for a, b in stock_picking_move_id[j].items():
#                 #         if a != 'id':
#                 #                 stock_prod_id_rec_list[j].append(b)
        
# print(stock_prod_id_rec_list)


# for i in stock_prod_id_rec_list:
#         if i :
#                 print(i)

print('\n\n')

# for i in range(len(stock_prod_id_rec_list)):
#         if stock_prod_id_rec_list[i]:
#                 var = stock_prod_id_rec_list[i]
#                 print(var)
#                 for j in range(3):
#                         print(var[j])

# print("\n")

# stock_prod_id_rec_list= []
# for i in range(len(stock_picking_move_id)):
#     stock_prod_id_rec_list.append([])
#     for a, b in stock_picking_move_id[i].items():
#         if a != 'id':
#             stock_prod_id_rec_list[i].append(b)

# print("\n\n\n")
# # print(stock_prod_id_rec_list)
# for i in stock_prod_id_rec_list:
#         print(i)

# for i in range(len(stock_prod_id_rec_list)):
#     for j in range(len(stock_prod_id_rec_list[i])):
#         print(stock_prod_id_rec_list[i])

        ## SQL CONNECTION ##

# conn = sql.connect(host="staging-db-for-all-clients-cluster.cluster-chtdjteevifq.us-east-1.rds.amazonaws.com", 
#         port="3306", user="anfords", password="A8g4t!&4b4YrW)$y", database="staging_anfords")

# cursor = conn.cursor()

# cursor.executemany("INSERT INTO autoda_receiving_copy (DONumber, OrderNumber, Quantity) VALUES (%s, %s, %s)", stock_prod_id_rec_list)
# # print(cursor.execute('SHOW GRANTS;'))
# conn.commit()
# print(cursor.rowcount, "was inserted.")
# cursor.close()
# conn.close

#         ## END SQL CONNECTION ##