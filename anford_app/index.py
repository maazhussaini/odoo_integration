from flask import Flask, render_template, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
import json
from flask_mail import Mail
from xmlrpc import client as xmlrpclib
import mysql.connector as sql

app = Flask(__name__)

@app.route('/')
def home():
    data = []
    data.append(sql_server())
    return render_template('index.html', data=data)


def sql_server():
    conn = sql.connect(host="staging-db-for-all-clients-cluster.cluster-chtdjteevifq.us-east-1.rds.amazonaws.com", 
            port="3306", user="anfords", password="A8g4t!&4b4YrW)$y", database="staging_anfords")

    order_lst=[]

    cursor = conn.cursor()

    cursor.execute("Select DISTINCT OrderNumber from primary_order_details where OrderDate ='2020,11,10'")
    data = cursor.fetchall()

    OrderNumber_lst=[]

    for i in range(len(data)):
        for j in data[i]:
            OrderNumber_lst.append(j)

    print(OrderNumber_lst)
    sku_lst = []
    for i in range(len(OrderNumber_lst)):
        sel_dist = """Select DISTINCT SKUCode from primary_order_details where OrderDate ='2020,11,10' AND OrderNumber = '%s'"""
        dist = cursor.execute(sel_dist % OrderNumber_lst[i])
        product = cursor.fetchall()
        sku_lst.append([])
        for j in range(len(product)):
                for k in product[j]:
                    sku_lst[i].append(k)


    print(sku_lst)

    dist_lst = []
    for i in range(len(OrderNumber_lst)):
        sel_dist = """Select DISTINCT DistirbutorCode from primary_order_details where OrderDate ='2020,11,10' AND OrderNumber = '%s'"""
        dist = cursor.execute(sel_dist % OrderNumber_lst[i])
        product = cursor.fetchall()
        dist_lst.append([])
        for j in range(len(product)):
            for k in product[j]:
                dist_lst[i].append(k)
                

    print(dist_lst)

    qty_lst = []
    for i in range(len(OrderNumber_lst)):
        sel_dist = """Select Quantity from primary_order_details where OrderDate ='2020,11,10' AND OrderNumber = '%s'"""
        dist = cursor.execute(sel_dist % OrderNumber_lst[i])
        product = cursor.fetchall()
        qty_lst.append([])
        for j in range(len(product)):
            for k in product[j]:
                qty_lst[i].append(k)

    print(qty_lst)

    cursor.close()
    conn.close

    data = processing(dist_lst, sku_lst, OrderNumber_lst, qty_lst)
    return data


def processing(dist_lst, sku_lst, OrderNumber_lst, qty_lst):
    """
    docstring
    """
         ## ODOO DATABASE CONNECTION ##

    url = 'http://localhost:8069'
    db = 'anfords_odoo'
    username = 'admin'
    password = 'admin'

            ## ODOO DATABASE CONNECTION END ##

        ## ODOO ##

    common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(url))
    models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(url))

    uid = common.login(db, username, password)

    var = common.version()

    models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(url))

    if len(dist_lst) == len(sku_lst):
        combo = []
        for i in range(len(OrderNumber_lst)):
            partner_id = models.execute_kw(db, uid, password, 'res.partner', 'search', 
                            [[['x_dist_code', '=', dist_lst[i]]]])

            product_id = models.execute_kw(db, uid, password, 'product.product', 'search',
                                [[['barcode', '=', sku_lst[i]]]])
                
                # if len(sku_lst[i]) == len(product_id):
                        
                #         print("True")
                # else:
                #         print("False")

            print(i, partner_id)
            part_id = partner_id[0]
            print(product_id)
            prod_line = []

            for j in range(len(product_id)):
                    prod_id = product_id[j]
                    qty = qty_lst[i]
                        # print(prod_id)
                    line = (0,0, {
                                'product_id':prod_id,
                                'product_uom_qty':qty[j]
                        })
                    prod_line.append(line)

            print(prod_line)
            sale_order = models.execute_kw(db, uid, password, 'sale.order', 'create',
                        [{      'partner_id': part_id,
                                'x_api_orderNumber': OrderNumber_lst[i],
                                'order_line':prod_line
                        }])

            sale_order_name = models.execute_kw(db, uid, password, 'sale.order', 'read',
                                [sale_order], {'fields': ['name']})

            
            for j in range(len(sale_order_name)):
                combo.append([])
                for key, val in sale_order_name[j].items():
                    if key != "id":
                        print(val)
                        # return combo[i].append(val)
                        return sku_lst[i+1]
            
            print(sale_order_name)
        # return combo


if __name__ == "__main__":
    app.run(debug=True)