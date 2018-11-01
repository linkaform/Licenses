# -*- coding: utf-8 -*-
# © <2017> <Quadit, S.A. de C.V.>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
# Coded by:
# Jose Patricio Villareal - josepato@linkaform.com
# Lazaro Rodriguez Triana - lazaro@quadit.mx

import random
import unittest
import psycopg2
import os
import binascii
import time
import xmlrpclib
import time

# class OpenerpTest(unittest.TestCase):

object = 'object'
host = 'localhost'
user = 'admin'
pwd = 'admin'
dbname = 'test2'


def getRandomOption(option_leng, start=0):
    option_leng = range(start, option_leng)
    random.shuffle(option_leng)
    opt = option_leng[0]
    return opt


def getCursorpsql(dbname, user, host, password):
    try:
        conn = psycopg2.connect("""
            dbname='%s' user='%s' host='%s' password='%s'""" % (
                dbname, user, host, password))
        cur = conn.cursor()
        return cur
    except:
        print "I am unable to connect to the database"


def getWSTiny(host, object, user, pwd, dbname):
    con = xmlrpclib.ServerProxy('http://%s:8069/xmlrpc/common' % (host))
    uid = con.login(dbname, user, pwd)
    con = xmlrpclib.ServerProxy('http://%s:8069/xmlrpc/%s' % (host, object),
                                allow_none=True)
    return con, uid, dbname, pwd


def getMethod(model='res.partner', metodo='search', args=[], args2=[],
              args3=[], args4=[]):
    con, uid2, dbname2, pwd2 = getWSTiny(host, object, user, pwd, dbname)
    if args4:
        res = con.execute(dbname, uid2, pwd2, model, metodo, args, args2,
                          args3, args4)
    elif args3:
        res = con.execute(dbname, uid2, pwd2, model, metodo, args, args2,
                          args3)
    elif args2:
        res = con.execute(dbname, uid2, pwd2, model, metodo, args, args2)
    else:
        res = con.execute(dbname, uid2, pwd2, model, metodo, args)
    return res


def arrange_product(options, products):
    # Gets random only
    qty = int(random.random()*100)
    if qty <= 1:
        qty = 2
    qty = getRandomOption(qty, start=1)
    prod_categories = products.keys()
    print 'prod_categories', prod_categories
    print 'products', products
    opt = getRandomOption(len(prod_categories))
    prods = products[prod_categories[opt]]
    opt2 = getRandomOption(len(prods))
    product_id = products[prod_categories[opt]][opt2]['id']
    products_mobil = getMethod(
        'product.product', 'get_products_price', product_id, client_id, qty)
    line = {'product_id': product_id,
            'price': products_mobil['price'],
            'qty': qty,
            'license_status': set_license_status(qty)}
    return line


def set_license_status(qty):
    license_status = []
    for a in range(qty):
        license_status.append(
            {'name': 'josepato@infosync.mx',
             'license_token': '07c8d901-cd6a-4bfe-9885-6bfa499c8bf8',
             'license_id': a,
             'user_id': 32,
             'action': 'renew'})
        return license_status


def setDatabaseToTest():
    journal_ids = getMethod('account.journal', 'search', [])
    getMethod('account.journal', 'write', journal_ids, {'e_invoice': False})
    # Sets email servers to test enviroment
    email_servers = getMethod('ir.mail_server', 'search', [])
    getMethod('ir.mail_server', 'write', email_servers, {
        'password': 'OZzGhstV5FM5R5nIv6mn4Q'})
    # Sets company to regular invoicing deactiating electronic invoice
    company = getMethod('res.company', 'search', [])
    getMethod('res.company', 'write', company, {
        'proveedor_cfd': 'propios_medios'})
    cron = getMethod('ir.cron', 'search', [])
    if cron:
        getMethod('ir.cron', 'write', cron, {'active': False})
        user = 'admin'
        pwd = 'admin'


setDatabaseToTest()

user = 'admin'
pwd = 'admin'


def getRandomClients():
    client_id = getMethod('res.partner', 'search', [
        ('customer', '=', 1),
        ('infosync_user_id', '>', 0)])
    infosync_user_id = getMethod('res.partner', 'read', client_id,
                                 ['infosync_user_id'])
    random.shuffle(infosync_user_id)
    return infosync_user_id

infosync_user_id = getRandomClients()

orders = {0: 0}
products_try = 0
while max(orders.values()) < 1 or sum(orders.values()) > 2:
    random.shuffle(infosync_user_id)
    client_id = infosync_user_id[0]['infosync_user_id']
    print 'cliente_id', client_id
    options = getMethod('product.product', 'get_payment_options')
    opt = getRandomOption(len(options))
    option_1 = options[opt]['id']
    products = getMethod('product.product', 'get_option_products',
                         option_1, client_id)
    print 'option', option_1
    print 'products', products
    opt = getRandomOption(2)
    recurrent = [True, False][opt]
    print "======================recurrent", recurrent
    cart_lines = []
    if not products:
        print 'NO PRODUCTS WITH OPTION ', option_1
        products_try += 1
        if products_try > 5:
            print 'BREAK cycle, more than 5 products where not found'
            break
        continue
    for record in range(getRandomOption(10, 1)):
        cart_lines.append(arrange_product(options, products))

    cart = {'recurrent': recurrent,
            'option': option_1,
            'cart': cart_lines}

    if random.random() <= .1:
        cart.update({'discount_code': 'Info Rocks'})
    print 'create cart'
    info_cart = getMethod('sale.order', 'infosync_create_cart', client_id,
                          cart)
    sale_order_id = info_cart['id']
    print 'saleorder id', sale_order_id
    licence_to_create = getMethod('sale.order', 'get_sale_order_licenses',
                                  sale_order_id)
    print 'licence_to_create', licence_to_create
    payment_confirmation = {
      'reference_id': sale_order_id,
      'amount': info_cart['amount_total'] * 100,
      'id': 'ID Concekta - ' + str(time.time()),
      'description': 'Descripcion de prueba de pago',
      # 'payment_method': 'credit_card',
    }
    credit_card = {
        u'exp_month':
        u'06',
        u'name':
        u'Emmanuel',
        u'brand': u'visa',
        u'object': u'card_payment',
        u'last4': u'4242',
        u'auth_code': u'000000',
        u'exp_year': u'18'}

    wire_transfer = {'object': 'wire_transfer'}

    opt = getRandomOption(2)
    print "opt", opt
    pay_method = [credit_card, wire_transfer][opt]
    print "pay_method", pay_method
    payment_confirmation = {u'status': u'paid', u'livemode': False,
                            u'description': u'Pago Infosync ', u'refunds': [],
                            u'pay_method': pay_method,
                            u'created_at': str(time.time()),
                            u'object': u'charge',
                            u'failure_message': False,
                            u'currency': u'MXN',
                            u'amount': info_cart['amount_total'] * 100,
                            u'fee': info_cart['amount_total'] * 100 * .04,
                            u'reference_id': sale_order_id,
                            u'failure_code': False,
                            u'customer_id':
                            u'cus_DrqoSPRCuSC33rXBf',
                            u'paid_at': str(time.time()+2),
                            'id': u'55031faa2412296988001a7c',
                            u'monthly_installments': False,
                            u'details': {
                                u'phone': False,
                                u'line_items': [],
                                u'name': False,
                                u'email': False}}
    print "payment_confirmation", payment_confirmation
    random_pay = random.random()
    print "random_pay", random_pay
    if random_pay > .7:
       getMethod('sale.order', 'confirm_sale_payment_ceditcard',
                 payment_confirmation, client_id)
       if orders.get(client_id, 0):
           orders[client_id] += 1
       else:
           orders[client_id] = 1
    else:
       print 'No pago la orden y dejo la el sale order en draft--------------'
