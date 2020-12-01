##      LIBERIES       ##

from xmlrpc import client as xmlrpclib
import mysql.connector as sql
from operator import itemgetter

        ## ODOO DATABASE CONNECTION ##

url = 'http://168.119.21.214:8069'
db = 'Image_API'
username = 'image@test.com'
password = 'Muhammad@786'

        ## CONNECTION END

        ## ODOO 

common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(url))
models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(url))

uid = common.login(db, username, password)

var = common.version()

models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(url))

stock_prod_records = models.execute_kw(db, uid, password,
    'stock.production.lot', 'search_read',
    [[]],
    {'fields': ['product_id']})

stock_prod_records_list = models.execute_kw(db, uid, password,
    'stock.production.lot', 'search_read',
    [[]],
    {'fields': ['name']})


stock_prod_id_rec_list= []
for i in range(len(stock_prod_records)):
        for a, b in stock_prod_records[i].items():
                if a == 'id':
                        stock_prod_id_rec_list.append(b)


stock_quant_records = models.execute_kw(db, uid, password,
    'stock.quant', 'search_read',
    [[['lot_id', '=', stock_prod_id_rec_list], ['location_id', '=',40 ]]],
    {'fields': ['location_id','product_id','lot_id']})



for i in stock_quant_records:
        del i['id']
        print(i)



print(len(stock_quant_records))    

rec_list=  []

for i in range(len(stock_quant_records)-1):
        for a, b in stock_quant_records[i].items():
                if a != 'id':
                        rec_list.append(b)
