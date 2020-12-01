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



order_line = []
for i in range(len(sale_order)):
    for k, j in sale_order[i].items():
        if k == 'order_line':
            order_line.append(j)

print("Order Line: ",order_line)


order_id= [] 
for k in range(len(sale_order)):
    for key, val in sale_order[k].items():
        if key != "id" and key != "order_line":
            if val.__class__ is list:
                order_id.append(val[1])
            else:
                order_id.append(val)
print("\n")
# print("Order ID: ",order_id)
for i in sale_order:
    print(i)
print("\n")
product_lst= []
sale_order_line = ""
for i in order_line:
    sale_order_line = models.execute_kw(db, uid, password,
        'sale.order.line', 'search_read',
        [[['id','=', i]]], {'fields': ['product_id']} )

    print("sale_order_line: ",sale_order_line)
    
    
    for k in range(len(sale_order_line)):
        product_lst.append([])
        for key, val in sale_order_line[k].items():
            if key != "id":
                if val.__class__ is list:
                    product_lst[k].append(val[1])
                else:
                    product_lst[k].append(val)

    
    print("product_lst: ",product_lst)
    # prod = ', '.join(product_lst)
    # print("prod: ",prod)
    # print("\n")

    product = []
    for sale_line in sale_order_line:
        product.append(sale_line['product_id'][0])
        # print(sale_line['product_id'])

    print("product: ",product)

#     categ_id = models.execute_kw(db, uid, password,
#         'product.product', 'search_read',
#         [[['id','=', product]]], {'fields': ['categ_id']} )

#     catg_lst= [] 
#     for k in range(len(categ_id)):
#         for key, val in categ_id[k].items():
#             if key != "id":
#                 if val.__class__ is list:
#                     catg_lst.append(val[1])
#                 else:
#                     catg_lst.append(val)

#     print(catg_lst)

#     print('\n')





# # &instructions=dummy%20instructions&no_of_flyers=1&stock_items=bg%3D20%2Cpen%3D100'

#     payload = 'account_id='+account_id+'&api_token='+api_token+'&service_type='+order_id[-1]+'&pickup_name='+order_id[1]+'&pickup_phone='+order_id[2]+'&pickup_address='+order_id[3]+'&pickup_city='+order_id[4]+'&delivery_name='+order_id[5]+'&delivery_phone='+order_id[6]+'&delivery_city='+order_id[7]+'&amount=1400&delivery_address='+order_id[8]+'&delivery_email=farhan.ahmadkhan@hotmail.com&reference_number='+order_id[0]+'&no_of_pieces=2&ensured_declared=&dimension_l=10&dimension_w=15&dimension_h=7&weight=2&item_detail='+prod
#     headers = {
#     'Content-Type': 'application/x-www-form-urlencoded'
#     }


#     response = requests.request("POST", api_url, headers=headers, data = payload)

#     forrun_res = response.text
#     print(forrun_res)

#     split_api = forrun_res.split(':')
#     api_order = split_api[-1]
#     api_order = api_order[1:-2]

#     sale_id = 0
#     for k in range(len(sale_order)):
#         for key, val in sale_order[k].items():
#             if key == "id":
#                 sale_id = val
    
#     write.write_cn_number(sale_id, api_order)