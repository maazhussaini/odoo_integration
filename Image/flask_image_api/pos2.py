#pip install Flask-JWT

from flask import Flask
from flask_restful import Resource, Api, reqparse, abort
from flask_httpauth import HTTPBasicAuth
import pandas as pd
from xmlrpc import client as xmlrpclib
import datetime
import json
from ast import literal_eval
from flask_jwt import JWT, jwt_required, current_identity
from werkzeug.security import safe_str_cmp
from functools import wraps

app = Flask(__name__)
api = Api(app)
auth = HTTPBasicAuth()


    ## SECURITY STARTPOINT ##

USER_DATA ={
    "admin":"SUPERSECRETKEY"
}

@auth.verify_password
def verify(username, password):
    if not (username and password):
        return False
    return USER_DATA.get(username) == password

class User(object):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

    def __str__(self):
        return "User(id='%s')" % self.id

users = [
    User(1, 'admin', 'Aff!n!ty@123')
]

username_table = {u.username: u for u in users}
userid_table = {u.id: u for u in users}

def authenticate(username, password):
    user = username_table.get(username, None)
    if user and safe_str_cmp(user.password.encode('utf-8'), password.encode('utf-8')):
        return user

def identity(payload):
    user_id = payload['identity']
    return userid_table.get(user_id, None)

app.config['SECRET_KEY'] = 'super-secret'

jwt = JWT(app, authenticate, identity)


def checkuser(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if current_identity.username == 'admin':
            return func(*args, **kwargs)
        return abort(401)
    return wrapper


        ## SECURITY ENDPOINT ##




class POS(Resource):

    decorators = [checkuser, jwt_required()]
    def post(self):
        parser = reqparse.RequestParser()  # initialize
        parser.add_argument('shopify_shipment_number', required=True)  # add arguments
        parser.add_argument('mode_of_payment', required=True)
        parser.add_argument('product', required=True)
        parser.add_argument('product_qty', required=True)
        parser.add_argument('discount', required=True)
        parser.add_argument('customer_name', required=True)
        parser.add_argument('customer_number', required=True)
        parser.add_argument('customer_address', required=True)

        args = parser.parse_args()  # parse arguments to dictionary

        ## ODOO DATABASE CONNECTION ##

        url = 'https://abs4.vdc.services'
        db = 'test_api'
        username = 'image@test.com'
        password = '12345'

            ##  ODOO    ##
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(url))
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(url))
        uid = common.login(db, username, password)

        
        ## CONNECTION END
        product = args['product']
        product_lst = list(map(str, product.split(', ')))
        print(len(product), product)
        print('product_lst: ', product_lst)

        product_qty = args['product_qty']
        product_qty_lst = list(map(int, product_qty.split(', ')))

        discount = args['discount']
        discount_lst = list(map(float, discount.split(', ')))
 
        partner_id = models.execute_kw(db, uid, password, 'res.partner', 'search', 
                                        [[['name', '=', args['customer_name']]]])

        if not partner_id:
            partner_id = models.execute_kw(db, uid, password, 'res.partner', 'create', [{
                        'name': args['customer_name'],'phone': args['customer_number']
                        }])

        print("partner_id: ", partner_id)
        print("Type partner_id: ", type(partner_id))

        if str(type(partner_id)) == "<class 'list'>":
            partner_id = int(partner_id[0])

        product_id_lst = []
        for i in product_lst:
            product_id = models.execute_kw(db, uid, password, 'product.template', 'search',
                                        [[['name', '=', i]]])
            if not product_id:
                return i + " not found"
            product_id_lst.append(product_id[0])
        
        
        print('product_id_lst: ',product_id_lst)

        product_list_price = []
        tax_id_lst = []
        product_prod_id_lst = []
        for i in product_id_lst:
            product_price = models.execute_kw(db, uid, password, 'product.product', 'search_read', [[['product_tmpl_id', '=', i]]],
                            {'fields': ['list_price', 'taxes_id']})

            print('product_price: ', product_price)
            for j in product_price:
                for key, val in j.items():
                    if key == 'id':
                        product_prod_id_lst.append(val)
                    if key == 'list_price':
                        print('List Price: ', val)
                        product_list_price.append(val)
                    if key == 'taxes_id':
                        tax_id_lst.append(val)
                        # for k in val:
                            

        print('tax_id_lst: ',tax_id_lst, len(tax_id_lst))
        for i in tax_id_lst:
            print(i)

        tax_amount_lst = []
        tax_name = []
        for i in range(len(tax_id_lst)):
            account_tax = models.execute_kw(db, uid, password, 'account.tax', 'search_read', [[['id', '=', tax_id_lst[i]]]],
                    {'fields': ['name','amount']})

            print('account_tax: ', account_tax)
            tax_amount_lst.append([])
            for j in account_tax:
                for key, val in j.items():
                    if key == 'name':
                        tax_name.append(val)
                    if key == 'amount':
                        tax_amount_lst[i].append(val)

        print('tax_amount_lst: ',tax_amount_lst)
        print('product_list_price: ', product_list_price)

        prod_line = []
        stock_move_line_line_lst = []
        operations_line_lst = []
        uom_id = 0

        payment_method = models.execute_kw(db, uid, password, 'pos.payment.method', 'search', [[['name', '=', args['mode_of_payment']]]])

        if not payment_method:
            return "Invalid Payment Method"

        print('payment_method: ',payment_method)

        uom_type = models.execute_kw(db, uid, password, 'product.template', 'search_read', [[['id', '=', product_id]]],
                    {'fields': ['uom_id']})
        for i in uom_type:
            for key, val in i.items():
                if key == 'uom_id':
                    uom_id = val[0]

        if len(product_id_lst) == len(product_qty_lst):
            total = []
            sub_total = 0
            discount = 0
            sum_tax_amount = []
            for j in range(len(product_prod_id_lst)):
                prod_id = product_prod_id_lst[j]
                print('prod_id: ',prod_id)
                qty = product_qty_lst[j]
                temp_total = (product_list_price[j] * qty)
                sub_total = temp_total

                print('sub_total before dis: ',sub_total)

                if discount_lst[j]:
                    if discount_lst[j] > 0:
                        disc_amount = (temp_total * discount_lst[j]) / 100
                        sub_total = temp_total - disc_amount
                sub_total_incl = sub_total
                print('sub_total after dis: ',sub_total)

                # sum_tax_amount.append(product_list_price[j] * qty * (sum(tax_amount_lst[j])/100))
                # temp = product_list_price[j] * qty * (sum(tax_amount_lst[j])/100)
                
                
                # sum_tax_amount.append(sub_total * (sum(tax_amount_lst[j])/100))
                # temp =sub_total * (sum(tax_amount_lst[j])/100)
                # total.append(sub_total + temp)
                # print('temp: ',temp)

                print('total after tax: ',total)

                tax_ids_after_fiscal_position = (1,15, 1)
                tax = sum(tax_amount_lst[j]) + 100
                sub_total_excl = (sub_total / tax) * 100
                sum_tax_amount.append(sub_total-sub_total_excl)
                total.append(sub_total)
                line = (0,0, {
                        'product_id': prod_id,
                        'qty':qty,
                        'tax_ids_after_fiscal_position': tax_id_lst[j],
                        'tax_ids':tax_id_lst[j],
                        'price_unit': product_list_price[j],
                        'discount': discount_lst[j],
                        'price_subtotal': sub_total_excl,
                        'price_subtotal_incl': sub_total
                })

                stock_move_line_line = (0,0,{
                                            'product_id': prod_id,
                                            'qty_done': qty,
                                            'location_id': 8,
                                            'product_uom_id': uom_id,
                                            'location_dest_id': 5
                                            # 'product_uom_qty': qty
                                        })
                operations_line = (0,0,{
                                    'name': args['shopify_shipment_number'], 
                                    'product_id': prod_id,
                                    # 'product_uom_qty': qty,
                                    # 'quantity_done': qty,
                                    'reserved_availability': qty,
                                    'product_uom': uom_id
                                    })
                prod_line.append(line)
                operations_line_lst.append(operations_line)
                stock_move_line_line_lst.append(stock_move_line_line)
                
                print(prod_line)

            print('sum_tax_amount: ',sum_tax_amount)
            date = datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S.%f')[:-7]
            print('date: ',date)
            
            payment_line = [(0,0,{
                'payment_date': date,
                'payment_method_id': payment_method[0],
                'amount':sum(total)
            })]
            print(payment_line)
            pos_order = models.execute_kw(db, uid, password, 'pos.order', 'create',
            [{      'partner_id': partner_id,
                    'x_shopify_shipment_number':args['shopify_shipment_number'],
                    'name': 'POS/00018',
                    'session_id': 18,
                    'amount_total': sum(total),
                    'amount_paid': sum(total),
                    'amount_return': 0,
                    'lines':prod_line,
                    'payment_ids':payment_line,
                    'amount_tax': sum(sum_tax_amount),
                    'state': 'paid'
            }])


            pos_order_line_id = models.execute_kw(db, uid, password, 'pos.order.line', 'search', [[['order_id', '=', pos_order]]])
            print('pos_order_line_id: ',pos_order_line_id)

            shopify_number = str(args['shopify_shipment_number'])
            print('shopify_number: ',shopify_number)

            stock_picking = models.execute_kw(db, uid, password, 'stock.picking', 'create',
                    [{
                            'partner_id': partner_id,
                            'picking_type_id': 16,
                            'location_id': 8,
                            'location_dest_id': 5  ,
                            # 'origin': str(args['shopify_shipment_number']),
                            # 'move_ids_without_package': operations_line_lst,
                            'move_line_ids_without_package': stock_move_line_line_lst,
                            'x_shopify_shipment_number': str(args['shopify_shipment_number'])
                            # 'immediate_transfer': 'f'

                    }])

            if pos_order:
                picking_name = models.execute_kw(db, uid, password, 'stock.picking', 'search_read',[[['id', '=', stock_picking]]],
                                {'fields': ['name']})
                stock_picking_name = ""
                for i in picking_name:
                    for key, val in i.items():
                        if key == 'name':
                            stock_picking_name = val

                update_picking = models.execute_kw(db, uid, password, 'stock.picking', 'write', [[stock_picking],{
                                'state': 'assigned'
                                }])
                update_pos_order = models.execute_kw(db, uid, password, 'pos.order', 'write', [[pos_order], {
                                    'location_id': 8, 'picking_id': stock_picking
                                    }])

                # validate_picking = models.execute_kw(db, uid, password,'stock.picking', 'button_validate',[stock_picking])
                # print('validate_picking: ',validate_picking)
                if update_pos_order == True:
                    return "{'status':'Order Successfully created'}", 200  # return data and 200 OK
            
            else:
                return "{'status': 'ERROR'}", 400
        else:
            return "Error in product / qty", 401

class FBR(Resource):
    
    @auth.login_required
    def get(self):
        parser = reqparse.RequestParser()  # initialize
        parser.add_argument('shopify_shipment_number', required=True)  # add arguments
        	# 0001
        args = parser.parse_args()  # parse arguments to dictionary
        print(args['shopify_shipment_number'])

        ## ODOO DATABASE CONNECTION ##

        url = 'https://abs4.vdc.services'
        db = 'test_api'
        username = 'image@test.com'
        password = '12345'

            ##  ODOO    ##
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(url))
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(url))
        uid = common.login(db, username, password)

        ## CONNECTION END
        
        shopify_shipment_number = models.execute_kw(db, uid, password, 'pos.order', 'search_read', [[['x_shopify_shipment_number', '=', args['shopify_shipment_number']]]],
                            {'fields': ['invoice_number']})

        invoice_number = {}
        for i in shopify_shipment_number:
            for key, val in i.items():
                if key !='id':
                    invoice_number[key] = val

        return invoice_number

class ReturnProduct(Resource):

    decorators = [checkuser, jwt_required()]
    def post(self):
        parser = reqparse.RequestParser()  # initialize
        parser.add_argument('x_shopify_shipment_number', required=True)  # add arguments

        args = parser.parse_args()  # parse arguments to dictionary
        print(args['x_shopify_shipment_number'])

        ## ODOO DATABASE CONNECTION ##

        url = 'https://abs4.vdc.services'
        db = 'test_api'
        username = 'image@test.com'
        password = '12345'

            ##  ODOO    ##
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(url))
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(url))
        uid = common.login(db, username, password)

        # CONNECTION END
        pos_order_id = models.execute_kw(db, uid, password,'pos.order', 'search_read', 
        [[['x_shopify_shipment_number', '=', args['x_shopify_shipment_number']]]],
                        {'fields': ['name','amount_tax', 'amount_total', 'amount_paid', 'lines', 'partner_id', 'picking_id', 'payment_ids']})
        
                    # 'partner_id': partner_id,
                    # 'x_shopify_shipment_number':args['shopify_shipment_number'],
                    # 'name': 'POS/00002',
                    # 'session_id': 2,
                    # 'amount_total': sum(total),
                    # 'amount_paid': sum(total),
                    # 'amount_return': 0,
                    # 'lines':prod_line,
                    # 'payment_ids':payment_line,
                    # 'amount_tax': sum(sum_tax_amount),
                    # 'state': 'paid'
        name = ""
        id = 0
        line = 0
        amount_tax = 0
        amount_total = 0
        amount_paid = 0
        partner_id = 0
        picking_id = 0
        payment_id = 0


        for i in pos_order_id:

            for key, val in i.items():
                if key == 'amount_tax':
                    amount_tax = val * (-1)
                if key == 'amount_total':
                    amount_total = val * (-1)
                if key == 'amount_paid':
                    amount_paid = val * (-1)
                if key == 'lines':
                    line = val[0]
                if key == 'picking_ids':
                    picking_ids = val[0]
                if key == 'partner_id':
                    partner_id = val[0]
                if key == 'id':
                    id = val
                if key == 'name':
                    name = val

        pos_line = models.execute_kw(db, uid, password, 'pos.order.line', 'search_read', [[['order_id', '=',id]]],
                    {'fields': ['product_id', 'qty', 'tax_ids_after_fiscal_position', 'tax_ids', 
                    'price_unit', 'discount', 'product_uom_id', 'price_subtotal', 'price_subtotal_incl']})

        pos_payment = models.execute_kw(db, uid, password, 'pos.payment', 'search_read', [[['pos_order_id', '=',id]]],
                    {'fields': ['payment_method_id']})
        print('\n\n')
        print(pos_line)
        print('\n\n')
        for i in pos_payment:
            for key, val in i.items():
                if key == 'payment_method_id':
                    payment_id = val[0]

        product_id = []
        price_subtotal = []
        price_subtotal_incl = []
        qty = []
        discount = []
        product_uom_id = []
        price_unit = []
        tax_ids_after_fiscal_position = []
        tax_ids = []

        for i in pos_line:
            for key, val in i.items():
                if key == 'product_id':
                    product_id.append(val[0])
                if key == 'qty':
                    qty.append(val * (-1))
                if key == 'discount':
                    discount.append(val)
                if key == 'product_uom_id':
                    product_uom_id.append(val[0])
                if key == 'price_subtotal':
                    price_subtotal.append(val* (-1))
                if key == 'price_subtotal_incl':
                    price_subtotal_incl.append(val* (-1))
                if key == 'price_unit':
                    price_unit.append(val)
                if key == 'tax_ids':
                    tax_ids.append(val)
                if key == 'tax_ids_after_fiscal_position':
                    tax_ids_after_fiscal_position.append(val)

        print('product_id: ',product_id)
        print('qty: ',qty)
        print('discount: ',discount)
        print('product_uom_qty: ',product_uom_id)
        print("\n\n")
        
        line_order = []
        operations_line_lst = []
        stock_move_line_line_lst = []
        for i in range(len(pos_line)):
            line = (0,0, {
                        'product_id': product_id[i],
                        'qty':qty[i],
                        'tax_ids_after_fiscal_position': tax_ids_after_fiscal_position[i],
                        'tax_ids': tax_ids[i],
                        'price_unit': price_unit[i],
                        'discount': discount[i],
                        'price_subtotal': price_subtotal[i],
                        'price_subtotal_incl': price_subtotal_incl[i]
                })
            operations_line = (0,0,{
                                'name': args['x_shopify_shipment_number'], 
                                'product_id': product_id[i],
                                'product_uom_qty': qty[i],
                                'quantity_done': qty[i],
                                'product_uom': product_uom_id[i]
                                })

            stock_move_line_line = (0,0,{
                                            'product_id': product_id[i],
                                            'qty_done': (qty[i] * (-1)),
                                            'location_id': 5,
                                            'product_uom_id': product_uom_id[i],
                                            'location_dest_id': 8
                                            # 'product_uom_qty': qty
                                        })

            line_order.append(line)
            operations_line_lst.append(operations_line)
            stock_move_line_line_lst.append(stock_move_line_line)
        
        print('line_order: ', line_order)
        print("\n\n")
        print('operations_line_lst: ',operations_line_lst)

        date = datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S.%f')[:-7]
        print('date: ',date)
        payment_line = [(0,0,{
                'payment_date': date,
                'payment_method_id': payment_id,
                'amount': amount_total
            })]

        print('payment_line: ',payment_line)

        pos_order = models.execute_kw(db, uid, password, 'pos.order', 'create',
            
            [{      'partner_id': partner_id,
                    'x_shopify_shipment_number':args['x_shopify_shipment_number'],
                    'name': 'POS/00018',
                    'session_id': 18,
                    'amount_total': amount_total,
                    'amount_paid': amount_paid,
                    'amount_return': 0,
                    'lines': line_order,
                    'payment_ids':payment_line,
                    'amount_tax': amount_tax,
                    'state': 'paid',
                    'return_ref': name
            }])
        
        stock_picking = models.execute_kw(db, uid, password, 'stock.picking', 'create',
                    [{
                            'partner_id': partner_id,
                            'picking_type_id': 16,
                            'location_id': 5,
                            'location_dest_id': 8,
                            # 'origin': str(args['x_shopify_shipment_number']),
                            'x_shopify_shipment_number': str(args['x_shopify_shipment_number']),
                            # 'move_ids_without_package': operations_line_lst
                            'move_line_ids_without_package': stock_move_line_line_lst

                    }])

        if pos_order:
            picking_name = models.execute_kw(db, uid, password, 'stock.picking', 'search_read',[[['id', '=', stock_picking]]],
                            {'fields': ['name']})
            stock_picking_name = ""
            for i in picking_name:
                for key, val in i.items():
                    if key == 'name':
                        stock_picking_name = val

            update_picking = models.execute_kw(db, uid, password, 'stock.picking', 'write', [[stock_picking],{
                            'state': 'posConfirm'
                            }])
            update_pos_order = models.execute_kw(db, uid, password, 'pos.order', 'write', [[pos_order], {
                                'location_id': 5, 'picking_id': stock_picking, 'return_status': 'fully_return'
                                }])
            return update_pos_order
                
        return pos_order

class PickingIn(Resource):
    
    def get(self):

        ## ODOO DATABASE CONNECTION ##

        url = 'https://abs4.vdc.services'
        db = 'Image_API'
        username = 'image@test.com'
        password = '12345'

            ##  ODOO    ##
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(url))
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(url))
        uid = common.login(db, username, password)

        ## CONNECTION END

                ## ODOO 

                ### SYSTEM DATE ###

        dstamp = datetime.datetime.now().timestamp()
        dt = datetime.datetime.fromtimestamp(dstamp)
        d_truncated = datetime.date(dt.year, dt.month, dt.day)

                ### END SYSTEM DATE ###

                ### PCIKING ID ###

        stock_picking_records = models.execute_kw(db, uid, password,
            'stock.picking', 'search_read',
            [[]],
            {'fields': ['name']})
        #     ['x_studio_api_date','=',str(d_truncated)]

        stock_picking_id_rec_list= []
        for i in range(len(stock_picking_records)):
                for a, b in stock_picking_records[i].items():
                        if a == 'id':
                                stock_picking_id_rec_list.append(b)

                        ### END PICKING ID ###

                        ### FETCHING FIELDS ON THE BASIS OF TODAY'S DATE AND PCIKING ID  ###

        stock_move_records = models.execute_kw(db, uid, password,
            'stock.move', 'search_read',
            [[['picking_id','=',stock_picking_id_rec_list], ['location_dest_id', '=', 'WH/E-Commerce']]],
            {'fields': ['picking_id', 'product_id', 'product_uom_qty', 'quantity_done']})

        # stock_move_line_records = models.execute_kw(db, uid, password,
        #     'stock.move.line', 'search_read',
        #     [[['picking_id','=',stock_picking_id_rec_list], ['location_dest_id', '=', 'WH/E-Commerce']]],
        #     {'fields': ['picking_id', 'product_id', 'qty_done']})

                        ### END ###

                ### DELETING ID OF MOVE LINE ###
        for i in stock_move_records:
            del i['id']
                ### END ###

                ### CONVERT INTO JSON FORMAT ###
        return stock_move_records, 200  # return data and 200 OK     

                ### END ###
    
    decorators = [checkuser, jwt_required()]
    def post(self):

        parser = reqparse.RequestParser()  # initialize
        parser.add_argument('picking_id', required=True)  # add arguments
        parser.add_argument('quantity_done', required=True)
        parser.add_argument('product', required=True)
        
        args = parser.parse_args()  # parse arguments to dictionary

        url = 'https://abs4.vdc.services'
        db = 'Image_API'
        username = 'image@test.com'
        password = '12345'

            ##  ODOO    ##
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(url))
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(url))
        uid = common.login(db, username, password)

        product = args['product']
        product_lst = list(map(str, product.split(', ')))

        product_id_lst = []
        for i in product_lst:
            product_id = models.execute_kw(db, uid, password, 'product.product', 'search',
                                        [[['name', '=', i]]])

            product_id_lst.append(product_id[0])

        print('product_id: ',product_id_lst)

        stock_picking_records = models.execute_kw(db, uid, password,
            'stock.picking', 'search_read',
            [[['name','=', args['picking_id']]]],
            {'fields': ['name']})

        print('stock_picking_records: ',stock_picking_records)

        stock_picking_id_rec_list= []
        for i in range(len(stock_picking_records)):
                for a, b in stock_picking_records[i].items():
                        if a == 'id':
                                stock_picking_id_rec_list.append(b)

        print('stock_picking_id_rec_list: ',stock_picking_id_rec_list)
        stock_move_records = models.execute_kw(db, uid, password,
            'stock.move', 'search_read',
            [[['picking_id','=',stock_picking_id_rec_list], ['location_dest_id', '=', 'WH/E-Commerce']]],
            {'fields': ['picking_id', 'product_id', 'product_uom_qty', 'quantity_done']})
        
        # print("stock_move_records: ",stock_move_records)
        for i in stock_move_records:
            print('stock_move_records: ',i)


        uom_qty = []
        prod_lst = []
        primary_id = []
        for i in range(len(stock_move_records)):
                for a, b in stock_move_records[i].items():
                        if a == 'product_id':
                                prod_lst.append(b[0])
                        if a == 'id':
                                primary_id.append(b)
                        if a == 'product_uom_qty':
                                print('product_uom_qty: ',b)
                                uom_qty.append(b)

        print('primary_id: ',primary_id)
        print("prod_lst: ",prod_lst)
        qty_done = args['quantity_done']
        qty_lst = list(map(int, qty_done.split(', ')))
        qty_done_write = ""

        print("\n\n")
        for i in range(len(stock_move_records)):
            for j in range(len(product_id_lst)):
                if prod_lst[i] == product_id_lst[j]:
                    print('prod_lst[i]: ',prod_lst[i], j, i)
                    print('primary_id[',i,']', primary_id[i], j ,i)
                    print('uom_qty[',i,']', uom_qty[i], j ,i)
                    print('qty_lst[',i,']', qty_lst[i], j ,i)
                    qty_done_write = models.execute_kw(db, uid, password, 'stock.move', 'write', [[primary_id[i]], {
                                    'product_uom_qty':uom_qty[i],'quantity_done': qty_lst[j]
                                    }])
            print("\n")

        

        button_confirm = models.execute_kw(db, uid, password, 'stock.picking', 'action_confirm', [stock_picking_id_rec_list])
        # button_validate = models.execute_kw(db, uid, password, 'stock.picking', 'write', [[stock_picking_id_rec_list[0]], {
        #         'x_validate': 't',
        # }])

        button_validate = models.execute_kw(db, uid, password, 'stock.picking', 'write', [[stock_picking_id_rec_list[0]], {
                'state': 'approved',
        }])
        print("\n\n")                       
        print("product_lst: ",product_lst)
        print("qty_done_write: ",qty_done_write)
        print('button_validate: ',button_validate)

        return button_confirm, 200  # return data and 200 OK   

class PickingOut(Resource):

    def get(self):

        ## ODOO DATABASE CONNECTION ##

        url = 'https://abs4.vdc.services'
        db = 'Image_API'
        username = 'image@test.com'
        password = '12345'

            ##  ODOO    ##
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(url))
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(url))
        uid = common.login(db, username, password)

        ## CONNECTION END

                ## ODOO 

                ### SYSTEM DATE ###

        dstamp = datetime.datetime.now().timestamp()
        dt = datetime.datetime.fromtimestamp(dstamp)
        d_truncated = datetime.date(dt.year, dt.month, dt.day)

                ### END SYSTEM DATE ###

                ### PCIKING ID ###

        stock_picking_records = models.execute_kw(db, uid, password,
            'stock.picking', 'search_read',
            [[]],
            {'fields': ['name']})
        #     ['x_studio_api_date','=',str(d_truncated)]

        stock_picking_id_rec_list= []
        for i in range(len(stock_picking_records)):
                for a, b in stock_picking_records[i].items():
                        if a == 'id':
                                stock_picking_id_rec_list.append(b)

                        ### END PICKING ID ###

                        ### FETCHING FIELDS ON THE BASIS OF TODAY'S DATE AND PCIKING ID  ###

        stock_move_records = models.execute_kw(db, uid, password,
            'stock.move', 'search_read',
            [[['picking_id','=',stock_picking_id_rec_list], ['location_dest_id', '=', 'WH/E-Commerce']]],
            {'fields': ['picking_id', 'product_id', 'product_uom_qty', 'quantity_done']})

                        ### END ###

                ### DELETING ID OF MOVE LINE ###
        for i in stock_move_records:
            del i['id']
                ### END ###

                ### CONVERT INTO JSON FORMAT ###
        return stock_move_records, 200  # return data and 200 OK     

                ### END ###
    
    decorators = [checkuser, jwt_required()]    
    def post(self):

        parser = reqparse.RequestParser()  # initialize
        parser.add_argument('picking_id', required=True)  # add arguments
        parser.add_argument('quantity_done', required=True)
        parser.add_argument('product', required=True)

        args = parser.parse_args()  # parse arguments to dictionary

        url = 'https://abs4.vdc.services'
        db = 'Image_API'
        username = 'image@test.com'
        password = '12345'

            ##  ODOO    ##
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(url))
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(url))
        uid = common.login(db, username, password)

        print(args['picking_id'])
        picking_id = args['picking_id']
        print("picking_id: ", picking_id)

        product = args['product']
        product_lst = list(map(str, product.split(', ')))

        product_id_lst = []
        for i in product_lst:
            product_id = models.execute_kw(db, uid, password, 'product.product', 'search',
                                        [[['name', '=', i]]])

            product_id_lst.append(product_id[0])

        stock_picking_records = models.execute_kw(db, uid, password,
            'stock.picking', 'search_read',
            [[['name','=', picking_id]]],
            {'fields': ['name']})

        print("stock_picking_records: ", stock_picking_records)
        stock_picking_id_rec_list= []
        for i in range(len(stock_picking_records)):
                for a, b in stock_picking_records[i].items():
                        if a == 'id':
                                stock_picking_id_rec_list.append(b)
        
        print("stock_picking_id_rec_list: ",stock_picking_id_rec_list)

        # , ['location_id', '=', 'WH/E-Commerce']
        stock_move_records = models.execute_kw(db, uid, password,
            'stock.move', 'search_read',
            [[['picking_id','=',stock_picking_id_rec_list]]],
            {'fields': ['picking_id', 'product_id', 'product_uom_qty', 'quantity_done']})
        
        print("stock_move_records: ",stock_move_records)


        prod_lst = []
        primary_id = []
        uom_qty = []
        for i in range(len(stock_move_records)):
                for a, b in stock_move_records[i].items():
                        if a == 'product_id':
                                prod_lst.append(b[0])
                        if a == 'id':
                                primary_id.append(b)
                        if a == 'product_uom_qty':
                                print('product_uom_qty: ',b)
                                uom_qty.append(b)

        print(primary_id)
        print("prod_lst: ",prod_lst)
        qty_done = args['quantity_done']
        qty_lst = list(map(int, qty_done.split(', ')))
        qty_done_write = ""
        if len(qty_lst) == len(prod_lst):
            # for i in range(len(product_lst)):
            #         print(prod_lst[i])
            #         qty_done_write = models.execute_kw(db, uid, password, 'stock.move', 'write', [[primary_id[i]], {
            #                         'quantity_done': product_lst[i]
            #                         }])

            print("\n\n")
            for i in range(len(stock_move_records)):
                for j in range(len(product_id_lst)):
                    if prod_lst[i] == product_id_lst[j]:
                        print('prod_lst[i]: ',prod_lst[i], j, i)
                        print('primary_id[',i,']', primary_id[i], j ,i)
                        print('uom_qty[',i,']', uom_qty[i], j ,i)
                        print('qty_lst[',i,']', qty_lst[i], j ,i)
                        qty_done_write = models.execute_kw(db, uid, password, 'stock.move', 'write', [[primary_id[i]], {
                                        'product_uom_qty':uom_qty[i],'quantity_done': qty_lst[j]
                                        }])
                print("\n")

            button_confirm = models.execute_kw(db, uid, password, 'stock.picking', 'action_confirm', [stock_picking_id_rec_list])
            # button_validate = models.execute_kw(db, uid, password, 'stock.picking', 'write', [[stock_picking_id_rec_list[0]], {
            #     'x_validate': 't',
            # }])

            button_validate = models.execute_kw(db, uid, password, 'stock.picking', 'write', [[stock_picking_id_rec_list[0]], {
                'state': 'approved',
            }])


            # state_done =  models.execute_kw(db, uid, password, 'stock.picking', 'write', [[stock_picking_id_rec_list[0]], {
            #                         'state': 'approved'
            #                         }])
            print("product_lst: ",product_lst)
            print("qty_done_write: ",qty_done_write)
            print(button_validate)

            return button_validate, 200  # return data and 200 OK



api.add_resource(POS, '/pos')
api.add_resource(FBR, '/fbr')
api.add_resource(ReturnProduct, '/return')
api.add_resource(PickingIn, '/picking_in')  # add endpoints
api.add_resource(PickingOut, '/picking_out')  # add endpoints

if __name__ == '__main__':
    app.run(debug=True)  # run our Flask app