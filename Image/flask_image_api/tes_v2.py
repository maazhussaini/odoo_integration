import requests
import hashlib
import hmac
import base64
from flask import Flask
from flask_restful import Resource, Api, reqparse, abort
from flask_httpauth import HTTPBasicAuth
import pandas as pd
from xmlrpc import client as xmlrpclib
from ast import literal_eval
from flask_jwt import JWT, jwt_required, current_identity
from werkzeug.security import safe_str_cmp
from functools import wraps


secret = b'xxx'

payload='{"batch_id":"wq4223","supplier": {"id": 1,"supplier_name": "supplier name","street_address": "supplier address","city": "supplier city","contact_no_1": "343232434","email": "supplier@email.com","contact_person_name": "John doe","postal_code": "110011","contact_no_2": "2132133"},"products": [{"sku": "dfdfd","batch_id": "dfdfd","qty": "1","item_name": "product name","unit_cost": "100","selling_price": "120","thumbnail_url": "http://www.example.com/product_image_url.jpg","reorder_level": "0","exp_date_applicable": "0","attributes": "[]"}]}'


print(payload.encode('utf-8'))

endpoint_str_in = 'str_in'
endpoint_str_out = 'str_out'
endpoint_str_cancel = 'str_cancel'

signature = base64.b64encode(hmac.new(secret, payload.encode('utf-8'), digestmod=hashlib.sha256).digest())
headers = {
  'x-tes-hmac-sha256': signature,
  'Accept': 'application/json',
  'Content-Type': 'application/json'
}

app = Flask(__name__)
api = Api(app)

class str_in(Resource):
  def post(self):
    payload='{"batch_id":"wq4223","supplier": {"id": 1,"supplier_name": "supplier name","street_address": "supplier address","city": "supplier city","contact_no_1": "343232434","email": "supplier@email.com","contact_person_name": "John doe","postal_code": "110011","contact_no_2": "2132133"},"products": [{"sku": "dfdfd","batch_id": "dfdfd","qty": "1","item_name": "product name","unit_cost": "100","selling_price": "120","thumbnail_url": "http://www.example.com/product_image_url.jpg","reorder_level": "0","exp_date_applicable": "0","attributes": "[]"}]}'
    url = "https://image.siardigital.com/crm/api/erp/"+endpoint_str_in
    response = requests.request("POST", url, headers=headers, data=payload)
    return {response.text}

class str_out(Resource):
  def post(self):
    payload = '{"transfer_id":"str123","supplier": {"id": 1,"supplier_name": "Dispatch location name","street_address": "Dispatch location address","city": "Dispatch location city","contact_no_1": "Dispatch location phone","email": "supplier@email.com","contact_person_name": "John doe","postal_code": "110011","contact_no_2": "Secondary phone number"},"products": [{"sku": "testsku1","qty": "2","item_name": "Test product one","unit_cost": "0","serialised": 0,"thumbnail_url": "https://cdn.example.com/files/pr1.png","batch_id": "b123"},{"sku": "testsku22","qty": "1","item_name": "Test product two","unit_cost": "0","serialised": 0,"thumbnail_url": "https://cdn.example.com/files/pr2.png","batch_id": "b124"}]}'
    url = "https://image.siardigital.com/crm/api/erp/"+endpoint_str_in
    response = requests.request("POST", url, headers=headers, data=payload)
    return {response.text}

class str_cancel(Resource):
  def post(self):
    payload = '{"transfer_id":"str123","supplier": {"id": 1,"supplier_name": "Dispatch location name","street_address": "Dispatch location address","city": "Dispatch location city","contact_no_1": "Dispatch location phone","email": "supplier@email.com","contact_person_name": "John doe","postal_code": "110011","contact_no_2": "Secondary phone number"},"products": [{"sku": "testsku1","qty": "2"},{"sku": "testsku22","qty": "5"}]}'
    url = "https://image.siardigital.com/crm/api/erp/"+endpoint_str_in
    response = requests.request("POST", url, headers=headers, data=payload)
    return {response.text}

api.add_resource(str_in, '/str_in')
api.add_resource(str_out, '/str_out')  # add endpoints
api.add_resource(str_cancel, '/str_cancel')  # add endpoints

if __name__ == '__main__':
    app.run(debug=True)  # run our Flask app