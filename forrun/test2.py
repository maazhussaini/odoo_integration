from xmlrpc import client as xmlrpclib
import requests
from requests import api
import write


        ## FORRUN CREDENTIALS ##
api_url = "https://forrun.co/api/v1/addnewOrder"
account_id = '10011'
api_token = '7wJCDcI9K6xdq8je2wv5iUrHbVg6opKr85CkTmOJj4A03KIrcGPEPVQxB0iK'

        ## END FORRUN CREDENTIALS ##

        ## ODOO CREDENTIALS ##

url = 'http://165.22.15.64:8069'
db = "ForrunDB"
username = 'farhan'
password = 'ArpatecH157'

        ##END ODOO CREDENTIALS ##

common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(url))
models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(url))
uid = common.login(db, username, password)


## Fetch sale order id where CN number is not null

cn_number_id = models.execute_kw(db, uid, password,
        'sale.order', 'search', [[['x_cn_number', '!=', '']]])

## Fetch sale order where above sale order id is not equal to the primary id

sale_order = models.execute_kw(db, uid, password,   
    'sale.order', 'search_read',
    [[["id", '!=', cn_number_id]]],
    {'fields': ['name','x_studio_pickup_name', 'x_studio_pickup_phone', 'x_studio_pickup_address', 'x_studio_pick_location', 
            'x_partner', 'x_phone', 'x_city', 'x_street', 'x_studio_service_type_1','order_line']})

## Seperating Order Line ID
order_line = []
print("Order Line: ",order_line)
print("\nSale Order: ")
for i in range(len(sale_order)):
    print(sale_order[i],"\n")
    for k, j in sale_order[i].items():
        if k == 'order_line':
            order_line.append(j)

print("\nOrder Line", order_line)

print("\n")

## Fetching product using order_line id
product_lst= []
for i in range(len(order_line)):
    sale_order_line = models.execute_kw(db, uid, password,
        'sale.order.line', 'search_read',
        [[['id','=', order_line[i]]]], {'fields': ['product_id']} )
        
    
    ## Separating product name
    product_lst.append([])
    for k in range(len(sale_order_line)):
        print("sale_order_line: ",sale_order_line[k])
        for key, val in sale_order_line[k].items():
            if key != "id":
                if val.__class__ is list:
                    product_lst[i].append(val[1])
                else:
                    product_lst[i].append(val)

    print("product_lst: ",product_lst)
    