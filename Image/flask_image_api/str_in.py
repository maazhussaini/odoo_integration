import requests
import hashlib
import hmac
import re
import base64
from xmlrpc import client as xmlrpclib
import json

def str_in():
    ## ODOO DATABASE CONNECTION ##

    url = 'https://abs4.vdc.services'
    db = 'test_api'
    username = 'image@test.com'
    password = '12345'

    ##  ODOO    ##

    common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(url))
    models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(url))
    uid = common.login(db, username, password)

    ## DEFINE VARIABLES
    
    move_ids_without_package_id_lst = []
    transfer_id = []
    partner_id = []
    product_id = []
    product_name = []
    product_uom_qty = []
    default_code = []
    name_lst = []
    address_lst = []
    phone_lst = []
    city_lst = []
    transfer = []
    product = []


    stock_picking_in_records = models.execute_kw(db, uid, password,
            'stock.picking', 'search_read',
            [[['location_dest_id','=', 'WH/E-Commerce'],['partner_id', '!=', False], ['x_tes_validate','!=', 't']]],
            {'fields': ['partner_id', 'name', 'move_ids_without_package', 'location_id', 'location_dest_id']})
    
    for i in stock_picking_in_records:
        move_ids_without_package_id_lst.append(i['move_ids_without_package'])
        transfer_id.append(i['name'])
        transfer.append(i['id'])
        partner_id.append(i['partner_id'][0])

    print('move_ids_without_package_id_lst: ',move_ids_without_package_id_lst)
    print('transfer_id: ',transfer_id)
    print('partner_id: ',partner_id)


    for index, values in enumerate(move_ids_without_package_id_lst):
        product_name.append([])
        product_uom_qty.append([])
        product_id.append([])
        default_code.append([])

        move_ids_without_package = models.execute_kw(db, uid, password,
                'stock.move', 'search_read',
                [[['id','=', values]]],
                {'fields': ['product_id', 'product_uom_qty', 'quantity_done']})
        for prod in move_ids_without_package:
            product_id[index].append(prod['product_id'][0])
            prod_name = re.findall(r'] (.*)',prod['product_id'][1])
            ref = re.findall(r'\[(.+?)\]',prod['product_id'][1])
            product_name[index].append(prod_name[0])
            default_code[index].append(ref[0])
            product_uom_qty[index].append(prod['product_uom_qty'])

    print("\n")
    for i in product_uom_qty:
        print("product_uom_qty: ",i)

    print("\n")
    for i in product_id:
        print("Product Id: ", i)

    print("\n")
    for prod in product_name:
        print('product_name: ',prod)

    print("\n")
    for ref in default_code:
        print('default_code: ',ref)

    for index, values in enumerate(partner_id):
        name_lst.append([])
        address_lst.append([])
        phone_lst.append([])
        city_lst.append([])

        partner = models.execute_kw(db, uid, password, 'res.partner', 'search_read', [[['id', '=', values]]], {'fields': ['id', 'name', 'street', 'state_id', 'zip', 'country_id', 'phone']})
        for cust in partner:
            name_lst[index].append(cust['name'])
            phone_lst[index].append(cust['phone'])
            if cust['state_id'] != False:
                city_lst[index].append(cust['state_id'][1])
            else:
                city_lst[index].append("None")

            if (cust['street'] and cust['state_id'] and cust['zip'] and cust['country_id']) != False:
                
                address = str(cust['street']) + ", " + str(cust['state_id'][1]) + ", " + str(cust['zip']) + ", " + str(cust['country_id'][1])
                address_lst[index].append(address)
            else:
                address_lst[index].append("None")

    print("\n")
    for i in city_lst:
        print('city_lst: ', i)

    print("\n")
    for i in range(len(address_lst)):
        print('address_lst: ',address_lst[i])

    print("\n")
    for i in name_lst:
        print("name_lst: ",i)

    print("\n")
    for i in phone_lst:
        print('Phone: ',i)


    if len(transfer_id) == ( len(partner_id) and len(product_id) ):
        
        ## FOR PRODUCT
        for index, values in enumerate(transfer_id):
            
            if len(product_name[index]) > 1:
                product.append([])
                for j in range(len(product_name[index])):
                    var = {}
                    var["sku"] = str(default_code[index][j])
                    var["qty"] = str(int(product_uom_qty[index][j]))
                    var["item_name"] = product_name[index][j]
                    product[index].append(var)
            
            else:
                product.append({})
                for j in range(len(product_name[index])):
                    product[index]["sku"] = str(default_code[index][j])
                    product[index]["qty"] = str(int(product_uom_qty[index][j]))
                    product[index]["item_name"] = str(product_name[index][j])

        ## For Supplier
        supplier = []
        for index, values in enumerate(name_lst):
            supplier.append({})
            for ind, val in enumerate(name_lst):
                supplier[index][str("id")] = partner_id[index]
                supplier[index][ str( "supplier_name")] = str(name_lst[index][0])
                supplier[index][str("street_address")] = str(address_lst[index][0])
                supplier[index][str("city")] = str(city_lst[index][0])
                supplier[index][str("contact_no_1")] = str(phone_lst[index][0])
                supplier[index][str("postal_code")] = "10011"

        ## FOR URL      
        for index, values in enumerate(transfer_id):
            if len(product_name[index]) > 1:
                secret = b'xxx'
            
                payload = '{"transfer_id": '+json.dumps(transfer_id[index])+',"supplier": '+str(json.dumps(supplier[index]))+',"products": '+str(json.dumps(product[index]) )+'}'
                url = "https://image.siardigital.com/crm/api/erp/str_in"
                signature = base64.b64encode(hmac.new(secret, payload.encode('utf-8'), digestmod=hashlib.sha256).digest())
                headers = {
                'x-tes-hmac-sha256': signature,
                'Accept': 'application/json',
                'Content-Type': 'application/json'
                }
                response = requests.request("POST", url, headers=headers, data=payload)
                resp = json.loads(response.text)
                if resp['success'] == 'true':

                    x_tes_validate = models.execute_kw(db, uid, password, 'stock.picking', 'write', [[transfer[index]], {
                            'x_tes_validate': "t"
                        }])
                    print(x_tes_validate)

            else:
                secret = b'xxx'
            
                payload = '{"transfer_id": '+json.dumps(transfer_id[index])+',"supplier": '+str(json.dumps(supplier[index]))+',"products": ['+str(json.dumps(product[index]) )+']}'
                url = "https://image.siardigital.com/crm/api/erp/str_in"
                signature = base64.b64encode(hmac.new(secret, payload.encode('utf-8'), digestmod=hashlib.sha256).digest())
                headers = {
                    'x-tes-hmac-sha256': signature,
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                }
                response = requests.request("POST", url, headers=headers, data=payload)
                resp = json.loads(response.text)
                if resp['success'] == 'true':
                    x_tes_validate = models.execute_kw(db, uid, password, 'stock.picking', 'write', [[transfer[index]], {
                            'x_tes_validate': "t"
                        }])
                    print(x_tes_validate)





str_in()