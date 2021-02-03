from flask import Flask
from flask_restful import Resource, Api, reqparse
import pandas as pd
import ast
from xmlrpc import client as xmlrpclib
import json
import datetime

app = Flask(__name__)
api = Api(app)


class PickingIn(Resource):

    def get(self):

        ## ODOO DATABASE CONNECTION ##

        url = 'http://168.119.21.214:8069'
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
    
    def post(self):

        parser = reqparse.RequestParser()  # initialize
        parser.add_argument('picking_id', required=True)  # add arguments
        parser.add_argument('quantity_done', required=True)
        parser.add_argument('product', required=True)
        
        args = parser.parse_args()  # parse arguments to dictionary

        url = 'http://168.119.21.214:8069'
        db = 'Image_API'
        username = 'image@test.com'
        password = '12345'

            ##  ODOO    ##
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(url))
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(url))
        uid = common.login(db, username, password)

        stock_picking_records = models.execute_kw(db, uid, password,
            'stock.picking', 'search_read',
            [[['name','=', args['picking_id']]]],
            {'fields': ['name']})

        stock_picking_id_rec_list= []
        for i in range(len(stock_picking_records)):
                for a, b in stock_picking_records[i].items():
                        if a == 'id':
                                stock_picking_id_rec_list.append(b)

        stock_move_records = models.execute_kw(db, uid, password,
            'stock.move', 'search_read',
            [[['picking_id','=',stock_picking_id_rec_list], ['location_dest_id', '=', 'WH/E-Commerce']]],
            {'fields': ['picking_id', 'product_id', 'product_uom_qty', 'quantity_done']})
        
        print("stock_move_records: ",stock_move_records)

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

        print(primary_id)
        print("prod_lst: ",prod_lst)
        qty_done = args['quantity_done']
        product_lst = list(map(int, qty_done.split(', ')))
        qty_done_write = ""
        for i in range(len(product_lst)):
                print(prod_lst[i])
                qty_done_write = models.execute_kw(db, uid, password, 'stock.move', 'write', [[primary_id[i]], {
                                'product_uom_qty':uom_qty[i],'quantity_done': product_lst[i]
                                      }])
                        # , 'state':'done'

        button_confirm = models.execute_kw(db, uid, password, 'stock.picking', 'action_confirm', [stock_picking_id_rec_list])
        button_validate = models.execute_kw(db, uid, password, 'stock.move', 'write', [[primary_id[0]], {
                'state':'done'
        }])                        
        print("product_lst: ",product_lst)
        print("qty_done_write: ",qty_done_write)
        print(button_validate)

        return stock_move_records, 200  # return data and 200 OK   

class PickingOut(Resource):

    def get(self):

        ## ODOO DATABASE CONNECTION ##

        url = 'http://168.119.21.214:8069'
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
    
    def post(self):

        parser = reqparse.RequestParser()  # initialize
        parser.add_argument('picking_id', required=True)  # add arguments
        parser.add_argument('quantity_done', required=True)
        parser.add_argument('product', required=True)

        args = parser.parse_args()  # parse arguments to dictionary

        url = 'http://168.119.21.214:8069'
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
        for i in range(len(stock_move_records)):
                for a, b in stock_move_records[i].items():
                        if a == 'product_id':
                                prod_lst.append(b[0])
                        if a == 'id':
                                primary_id.append(b)

        print(primary_id)
        print("prod_lst: ",prod_lst)
        qty_done = args['quantity_done']
        product_lst = list(map(int, qty_done.split(', ')))
        qty_done_write = ""
        for i in range(len(product_lst)):
                
                print(prod_lst[i])
                qty_done_write = models.execute_kw(db, uid, password, 'stock.move', 'write', [[primary_id[i]], {
                                'quantity_done': product_lst[i]
                                }])
        #                 # , 'state': 'done'
        
        state_done =  models.execute_kw(db, uid, password, 'stock.picking', 'write', [[stock_picking_id_rec_list[0]], {
                                'state': 'done'
                                }])
        print("product_lst: ",product_lst)
        print("qty_done_write: ",qty_done_write)
        print(state_done)

        return stock_move_records, 200  # return data and 200 OK   


api.add_resource(PickingIn, '/picking_in')  # add endpoints
api.add_resource(PickingOut, '/picking_out')  # add endpoints

if __name__ == '__main__':
    app.run(debug=True)  # run our Flask app