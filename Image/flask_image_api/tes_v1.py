import requests
import hashlib
import hmac
import base64

secret = b'xxx'

# payload='{"batch_id":"wq4223","supplier": {"id": 1,"supplier_name": "supplier name","street_address": "supplier address","city": "supplier city","contact_no_1": "343232434","email": "supplier@email.com","contact_person_name": "John doe","postal_code": "110011","contact_no_2": "2132133"},"products": [{"sku": "dfdfd","batch_id": "dfdfd","qty": "1","item_name": "product name","unit_cost": "100","selling_price": "120","thumbnail_url": "http://www.example.com/product_image_url.jpg","reorder_level": "0","exp_date_applicable": "0","attributes": "[]"}]}'
payload = '{"transfer_id":"str123","supplier": {"id": 1,"supplier_name": "Dispatch location name","street_address": "Dispatch location address","city": "Dispatch location city","contact_no_1": "Dispatch location phone","email": "supplier@email.com","contact_person_name": "John doe","postal_code": "110011","contact_no_2": "Secondary phone number"},"products": [{"sku": "testsku1","qty": "2","item_name": "Test product one","unit_cost": "0","serialised": 0,"thumbnail_url": "https://cdn.example.com/files/pr1.png","batch_id": "b123"},{"sku": "testsku22","qty": "1","item_name": "Test product two","unit_cost": "0","serialised": 0,"thumbnail_url": "https://cdn.example.com/files/pr2.png","batch_id": "b124"}]}'
signature = base64.b64encode(hmac.new(secret, payload.encode('utf-8'), digestmod=hashlib.sha256).digest())

print(payload.encode('utf-8'))
print("\n\n")
print(payload)

endpoint_str_in = 'str_in'
endpoint_str_out = 'str_out'
url = "https://image.siardigital.com/crm/api/erp/"+endpoint_str_in


headers = {
  'x-tes-hmac-sha256': signature,
  'Accept': 'application/json',
  'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)