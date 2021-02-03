import requests
from xmlrpc import client as xmlrpclib
import schedule
import time


def new_ticket():

    hd_id = []
    shipment_number = []
    ticket_number = []
    phone = []
    body = []

    # ODOO DATABASE CONNECTION ##

    url = 'http://oddoapp.forrun.co:8069'
    db = 'helpdesk'
    username = 'farhan'
    password = 'ArpatecH157'

        ##  ODOO    ##
    common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(url))
    models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(url))
    uid = common.login(db, username, password)

# ['x_studio_check', '=', '0'], ['stage_id','=', 'New']
    hd = models.execute_kw(db, uid, password, 'helpdesk.ticket', 'search_read',
                [[]],
                {'fields': ['x_studio_shipment_number', 'x_studio_ticket_sequence', 'x_studio_phone_1', 'x_studio_check', 'stage_id']})

    if hd:
        for i in hd:
            print(i)
            for key, val in i.items():
                if key == 'x_studio_shipment_number':
                    shipment_number.append(val)
                if key == 'x_studio_ticket_sequence':
                    ticket_number.append(val)
                if key == 'x_studio_phone_1':
                    phone.append(val)
                if key == 'id':
                    hd_id.append(val)

    if shipment_number:
        for i in range(len(shipment_number)):
            text = ""
            text = 'Dear customer,\n\n'
            text += 'New Ticket,\n'
            text += 'Your shipment number is '+str(shipment_number[i])+'.\n'
            text += 'And your ticket number is '+str(ticket_number[i])
            text += '.\n\nThank You'
            body.append(text)

    
    if hd:
        # len(body)
        for i in range(1):
# +str(phone[i])+
            url = "https://pk.eocean.us/APIManagement/API/RequestAPI?user=Taza_Mart&pwd=AHnRYeFaCqdNs%2fSunnnkSiIrujTNSS6zQKPIwZuziz5zZ0hw7uMYkSl8J9h7uxhxlg%3d%3d&sender=Forrun&reciever=03455560701&msg-data="+str(body[i])+"&response=string"
            
            payload={} #Use when data is needed to send
            headers = {} #for authentication
            
            response = requests.request("GET", url, headers=headers, data=payload)
            
            temp = response.text
            lst = temp.split(" ")
            print(len(lst))
            
            if len(lst) == 29:
                print(lst[2])
                sms_check = models.execute_kw(db, uid, password, 'helpdesk.ticket', 'write', [[hd_id[i]], {
                    'x_studio_check': '1'}])
                print(sms_check)
                print(ticket_number[i])
            elif len(lst) == 4:
                print(lst[0])
            else:
                error = {'Error': 'Contact with Technical Support'}
                print(error)
                print(lst)

    else:
        print("NO RECORDS")



def resolved_ticket():

    hd_id = []
    shipment_number = []
    ticket_number = []
    phone = []
    body = []

    # ODOO DATABASE CONNECTION ##

    url = 'http://oddoapp.forrun.co:8069'
    db = 'helpdesk'
    username = 'farhan'
    password = 'ArpatecH157'

        ##  ODOO    ##
    common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(url))
    models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(url))
    uid = common.login(db, username, password)


    hd = models.execute_kw(db, uid, password, 'helpdesk.ticket', 'search_read',
                [[['x_studio_check', '=', '1'], ['stage_id','=', 'Resolved']]],
                {'fields': ['x_studio_shipment_number', 'x_studio_ticket_sequence', 'x_studio_phone_1', 'x_studio_check', 'stage_id']})

    if hd:
        for i in hd:
            print(i)
            for key, val in i.items():
                if key == 'x_studio_shipment_number':
                    shipment_number.append(val)
                if key == 'x_studio_ticket_sequence':
                    ticket_number.append(val)
                if key == 'x_studio_phone_1':
                    phone.append(val)
                if key == 'id':
                    hd_id.append(val)

    if shipment_number:
        for i in range(len(shipment_number)):
            text = ""
            text = 'Dear customer,\n\n'
            text += 'Resolved Ticket,\n'
            text += 'Your shipment number is '+str(shipment_number[i])+'.\n'
            text += 'And your ticket number is '+str(ticket_number[i])
            text += '.\n\nThank You'
            body.append(text)

    
    if hd:
        for i in range(len(body)):

            url = "https://pk.eocean.us/APIManagement/API/RequestAPI?user=Taza_Mart&pwd=AHnRYeFaCqdNs%2fSunnnkSiIrujTNSS6zQKPIwZuziz5zZ0hw7uMYkSl8J9h7uxhxlg%3d%3d&sender=Forrun&reciever="+str(phone[i])+"&msg-data="+str(body[i])+"&response=string"
            
            payload={}
            headers = {}
            
            response = requests.request("GET", url, headers=headers, data=payload)
            
            temp = response.text
            lst = temp.split(" ")
            print(len(lst))
            
            if len(lst) == 29:
                print(lst[2])
                sms_check = models.execute_kw(db, uid, password, 'helpdesk.ticket', 'write', [[hd_id[i]], {
                    'x_studio_check': '0'}])
                print(sms_check)
                print(ticket_number[i])
            elif len(lst) == 4:
                print(lst[0])
            else:
                error = {'Error': 'Contact with Technical Support'}
                print(error)
                print(lst)

    else:
        print("NO RECORDS")



new_ticket()
resolved_ticket()
