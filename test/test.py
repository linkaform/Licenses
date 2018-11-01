import random
import unittest

import psycopg2
import os
import binascii
import time
import xmlrpclib
import time

object = 'object'
host = 'localhost'
user = 'admin'
pwd = 'admin'
dbname = 'odoo_test'
client_id = 9

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



res = getMethod('lkf.lisences','create_in_database')