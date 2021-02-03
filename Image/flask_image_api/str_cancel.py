import requests
import hashlib
import hmac
import re
import base64
from xmlrpc import client as xmlrpclib
import json

def str_cancel():
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
    name = []

    stock_picking_in_records = models.execute_kw(db, uid, password,
            'stock.picking', 'search_read',
            [[  ]],
            {'fields': ['name', 'location_id', 'location_dest_id']})
    # ['location_id','=', 'WH/E-Commerce']
    
    for i in stock_picking_in_records:
        if i['location_id'][1] == 'WH/E-Commerce':
            name.append(i['location_id'][1])
        elif i['location_dest_id'][1] == 'WH/E-Commerce':
            name.append(i['location_dest_id'][1])

    for doc_name in name:
        secret = b'xxx'
            
        payload = '{"transfer_id": '+json.dumps(doc_name)+'}'
        url = "https://image.siardigital.com/crm/api/erp/str_cancel"
        signature = base64.b64encode(hmac.new(secret, payload.encode('utf-8'), digestmod=hashlib.sha256).digest())
        headers = {
        'x-tes-hmac-sha256': signature,
        'Accept': 'application/json',
        'Content-Type': 'application/json'
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        print(response.text)

str_cancel()