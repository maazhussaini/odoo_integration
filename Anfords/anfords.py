# #! C:\Users\Syed Maaz Hussaini\AppData\Local\Programs\Python\Python39\python.exe
# print("Context-type: text/html\n\n");
# ##      LIBERIES       ##

# from xmlrpc import client as xmlrpclib
# import json
# import datetime

#         ## ODOO DATABASE CONNECTION ##

# url = 'http://168.119.21.214:8069'
# db = 'anfords_odoo'
# username = 'image@test.com'
# password = '12345'

#         ## CONNECTION END

#         ## ODOO 

# common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(url))
# models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(url))

# uid = common.login(db, username, password)

# var = common.version()

# models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(url))

#         ### PCIKING ID ###

# stock_picking_records = models.execute_kw(db, uid, password,
#     'res.partner', 'search_read',
#     [[['mobile','!=','']]],
#     {'fields': ['name', 'mobile']})

# stock_picking_id_rec_list= []
# for i in range(len(stock_picking_records)):
#         for a, b in stock_picking_records[i].items():
#                 if a == 'id':
#                         stock_picking_id_rec_list.append(b)



where = 20
speed = 50
print ("On your journey to %s, you drove at an average speed of %s miles per hour."% (where, speed))