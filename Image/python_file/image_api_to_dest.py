
##      LIBERIES       ##

from xmlrpc import client as xmlrpclib
import mysql.connector as sql
import json
import datetime

        ## ODOO DATABASE CONNECTION ##

url = 'http://168.119.21.214:8069'
db = 'Image_API'
username = 'image@test.com'
password = '12345'

        ## CONNECTION END

        ## ODOO 

common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(url))
models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(url))

uid = common.login(db, username, password)

var = common.version()

models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(url))

        ### SYSTEM DATE ###

dstamp = datetime.datetime.now().timestamp()
dt = datetime.datetime.fromtimestamp(dstamp)
d_truncated = datetime.date(dt.year, dt.month, dt.day)

        ### END SYSTEM DATE ###

        ### PCIKING ID ###

stock_picking_records = models.execute_kw(db, uid, password,
    'stock.picking', 'search_read',
    [[]],
    {'fields': ['name']})
#     ['x_studio_api_date','=',str(d_truncated)]

stock_picking_id_rec_list= []
for i in range(len(stock_picking_records)):
        for a, b in stock_picking_records[i].items():
                if a == 'id':
                        stock_picking_id_rec_list.append(b)

print(len(stock_picking_id_rec_list))

                ### END PICKING ID ###

                ### FETCHING FIELDS ON THE BASIS OF TODAY'S DATE AND PCIKING ID  ###

stock_move_line_records = models.execute_kw(db, uid, password,
    'stock.move.line', 'search_read',
    [[['picking_id','=',stock_picking_id_rec_list], ['location_id', '=', 'WH/E-Commerce']]],
    {'fields': ['picking_id', 'product_id', 'qty_done', 'location_id', 'location_dest_id', 'create_date']})

                ### END ###

        ### DELETING ID OF MOVE LINE ###
for i in stock_move_line_records:
    del i['id']

        ### END ###

        ### CONVERT INTO JSON FORMAT ###
print(json.dumps(stock_move_line_records, indent=2, sort_keys = True))     

        ### END ###
