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
print("\nSale Order: ")
for i in range(len(sale_order)):
    print(sale_order[i],"\n")
    for k, j in sale_order[i].items():
        if k == 'order_line':
            order_line.append(j)

print("\nOrder Line(order_line): ", order_line)

print("\n")

## Fetching product using order_line id
product_lst= []
id_lst = []
product_catg_id = []
for i in range(len(order_line)):
    sale_order_line = models.execute_kw(db, uid, password,
        'sale.order.line', 'search_read',
        [[['id','=', order_line[i]]]], {'fields': ['product_id']} )
        
    
    ## Separating product name
    product_lst.append([])
    id_lst.append([])
    product_catg_id.append([])
    for k in range(len(sale_order_line)):
        print("sale_order_line: ",sale_order_line[k])
        for key, val in sale_order_line[k].items():
            if key != "id":
                if val.__class__ is list:
                    product_lst[i].append(val[1])
                    # print("Maaz: ",val[0])
                    product_catg_id[i].append(val[0])
                else:
                    product_lst[i].append(val)
                    print("Maaz: ",product_lst[i])
            elif key == "id":
                id_lst[i].append(val)

    print("product_lst(product_lst): ",product_lst)
    print("Product Id(id_lst): ", id_lst)
    print("Product Catg ID(product_catg_id): ",product_catg_id)

    print("\n")
    prod = ""
    for k in product_lst:
        for j in k:
           prod = j
           print("Product Name(prod): ",prod)
    print("\n\n")
        # print(sale_order[i]['name'],"\n")

    print(sale_order[i]['x_studio_service_type_1'])
    print( sale_order[i]['x_studio_pickup_name'] )
    print(sale_order[i]['x_studio_pickup_phone'])
    print(sale_order[i]['x_studio_pickup_address'])
    print(sale_order[i]['x_studio_pick_location'][1])
    print(sale_order[i]['x_partner'])
    print(sale_order[i]['x_city'])
    print(sale_order[i]['x_phone'])
    print(sale_order[i]['x_street'])
    print(prod)
    print(sale_order[i]['name'])
    print("\n")
    if len(order_line) == len(sale_order):

        payload = 'account_id='+account_id+'&api_token='+api_token+'&service_type='+ sale_order[i]['x_studio_service_type_1'] +'&pickup_name='+ sale_order[i]['x_studio_pickup_name'] +'&pickup_phone='+ sale_order[i]['x_studio_pickup_phone'] +'&pickup_address='+ sale_order[i]['x_studio_pickup_address'][1] +'&pickup_city='+ sale_order[i]['x_studio_pick_location'][1] +'&delivery_name='+ sale_order[i]['x_partner'][1] +'&delivery_phone='+ sale_order[i]['x_phone'] +'&delivery_city='+ sale_order[i]['x_city'] +'&amount=1400&delivery_address='+ sale_order[i]['x_street'] +'&delivery_email=farhan.ahmadkhan@hotmail.com&reference_number='+ sale_order[i]['name'] +'&no_of_pieces=2&ensured_declared=&dimension_l=10&dimension_w=15&dimension_h=7&weight=2&item_detail='+prod
        headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
        }

        response = requests.request("POST", api_url, headers=headers, data = payload)

        forrun_res = response.text
        print(forrun_res)

        split_api = forrun_res.split(':')
        api_order = split_api[-1]
        api_order = api_order[1:-2]

        sale_id = 0
        for k in range(len(sale_order)):
            for key, val in sale_order[k].items():
                if key == "id":
                    sale_id = val
        
        write.write_cn_number(sale_id, api_order)