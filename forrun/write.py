from xmlrpc import client as xmlrpclib

from requests import api

url = 'http://165.22.15.64:8069'
db = "ForrunDB"
username = 'farhan'
password = 'ArpatecH157'

common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(url))
models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(url))
uid = common.login(db, username, password)

def write_cn_number(sale_number, api_order):
    print(sale_number, api_order)
    sale_order = models.execute_kw(db, uid, password, 'sale.order', 'write', [[sale_number], {
        'x_cn_number': api_order
    }])
    print(sale_order)
