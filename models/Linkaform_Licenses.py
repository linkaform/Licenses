# -*- coding: utf-8 -*-
import requests, simplejson, json
import  datetime
from dateutil.relativedelta import relativedelta

from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo import models, fields, api
from ast import literal_eval

getLicenses = 'https://zato.linkaform.com/api/126/get_account_license'
createLiccenses = 'https://zato.linkaform.com/api/126/create_license'
updateLicence = 'https://zato.linkaform.com/api/126/update_license'

class linkaform_licenses(models.Model):
    _name = 'lkf.licenses'


    owner_id = fields.Many2one(comodel_name='lkf.users', string='Owner',required=True)
    user_id = fields.Many2one(comodel_name='lkf.users', string='User',  domain= lambda self:self._get_users(),required=True)
    user_email = fields.Char()  #(compute='_set_user_email')
    user_name = fields.Char()  #(compute='_set_user_name')
    connection_name = fields.Many2one(comodel_name='lkf.users', string='Connection Name') #compute='_set_connection'
    token = fields.Char()
    expiration = fields.Date(required=True)
    is_active = fields.Boolean()
    plan_id = fields.Char()
    product_id = fields.Many2one(comodel_name="product.product",required=True)
    subscription_id = fields.Integer()
    update_at = fields.Date()
    properties  = fields.Text()
    number = fields.Integer(string="N° de Licencias")

    @api.multi
    @api.onchange('owner_id','connection_name')
    def _get_users(self):
        owener = self.owner_id.id
        connection = self.connection_name.id
        res = {}
        if self.connection_name:
            model = self.env['lkf.users']
            res['domain'] = {'user_id':['|',("parent_id", "=", connection),('id','=',connection)]}
        else:
            model = self.env['lkf.users']
            res['domain'] = {'user_id':['|',("parent_id", "=", owener),('id','=',owener)]}
        return res

    @api.onchange('user_id')
    @api.depends('user_id')
    def _set_user_name(self):
        self.user_name = self.user_id.name

    @api.onchange('user_id')
    @api.depends('user_id')
    def _set_user_email(self):
        self.user_email = self.user_id.email

    # @api.onchange('owener')
    # def _set_user_email(self):
    #     self.connection_name = self.owener.name
    # @api.onchange('owener')
    # def _set_user_email(self):
    #     self.connection_name = self.owener.name

    @api.onchange('product_id')
    def _product_exp(self):
        duration = self.product_id.attribute_value_ids.name
        if duration == 'Mensual':
            self.expiration = (datetime.datetime.now() + relativedelta(months=+1)).strftime("%Y-%m-%d")
        if duration == 'Trimestral':
            self.expiration = (datetime.datetime.now() + relativedelta(months=+3)).strftime("%Y-%m-%d")
        if duration == 'Semestral':
            self.expiration = (datetime.datetime.now() + relativedelta(months=+6)).strftime("%Y-%m-%d")
        if duration == 'Anual':
            self.expiration = (datetime.datetime.now() + relativedelta(years=+1)).strftime("%Y-%m-%d")

    @api.model
    def cron_licences(self):
        self.create_in_database()

    @api.model
    def create_in_database(self):
        query = 'delete from lkf_licenses'
        self.env.cr.execute(query)
        res = self.connect_to_service()
        for item in res:
            owner_id = item['connection_id']
            user_id = item['user_id']
            token = item['token']
            expiration = item['expiration']
            is_active = True
            plan_id = item['plan_id']
            product_id = item['product_id']
            subscription_id = 0
            ids = item['id']
            user_email = item['user_email']
            user_name = item['user_name']
            connection_id = item['connection_id']
            update_at = datetime.datetime.now().strftime("%Y-%m-%d")
            properties = item['properties']

            licenses = self.env.cr.execute("""INSERT INTO lkf_licenses (id,owner_id,user_id,user_email,user_name,connection_name,token,expiration,is_active,plan_id,product_id,subscription_id,update_at,properties) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",(ids,owner_id,user_id,user_email,user_name,connection_id,token,expiration,is_active,plan_id,product_id,subscription_id,update_at,properties))


        return True

    def connect_to_service(self):
        url = getLicenses
        headers = {'Content-type': 'application/json','Authorization': 'simon_carnal'}
        response = {'data':{}, 'status_code':''}

        r = requests.get(url,headers=headers)
        response['status_code'] = r.status_code

        if r.status_code == 200:
            r_data = simplejson.loads(r.content)
            if r_data.has_key('objects'):
                response['data'] = r_data['objects']
            else:
                response['data'] = r_data
        return response['data']['response']['response']


    @api.model
    def create(self,values):
        url = createLiccenses
        headers = {'Content-type': 'application/json','Authorization': 'simon_carnal'}
        response = {'data':{}, 'status_code':''}
        objeto = {
                "account_id": values['owner_id'],
                "user_id":values['user_id'],
                "product_id":values['product_id'],
                "expiration": values['expiration']
            }

        if values['connection_name']:
            objeto["connection_id"] = values['connection_name']
        if values['number']:
            objeto['qty'] = values['number']

        values['update_at'] = datetime.datetime.now().strftime("%Y-%m-%d")

        r = requests.post(url,simplejson.dumps(objeto),headers=headers)
        res = ""
        if r.status_code == 200:
            r_data = simplejson.loads(r.content)
            response['data'] = r_data
            for tokens in response['data']['response']['response']['token']:
                values['token'] = tokens
                res = super(linkaform_licenses,self).create(values)
        return res


    @api.multi
    def write(self,values):
        url = updateLicence
        headers = {'Content-type': 'application/json','Authorization': 'simon_carnal'}
        lic = self.search([('id','=',self.id)])
        data = {'license_token':lic.token}

        print 'vaaaaaaaaaaaaaaaaaaaaaaaaaalueeeeeeeeeeees', values
        if values.has_key('owner_id'):
            data['account_id'] = values['owner_id']

        if values.has_key('expiration'):
            data['expiration'] = values['expiration']

        if values.has_key('connection_id'):
            data['connection_id'] = values['connection_id']

        if values.has_key('user_id'):
            data['user_id'] = values['user_id']

        if values.has_key('product_id'):
            data['product_id'] = values['product_id']

        if values.has_key('properties'):
            data['properties'] = values['properties']

        values['update_at'] = datetime.datetime.now().strftime("%Y-%m-%d")

        r = requests.patch(url,simplejson.dumps(data),headers=headers)

        res = super(linkaform_licenses,self).write(values)




class ResPartner(models.Model):
    _inherit = 'res.partner'

    def acction_view_licenses(self):
        self.ensure_one()
        action = self.env.ref('linkaform_licenses.action_license_tree').read()[0]
        # action['domain'] = literal_eval(action['domain'])
        # action['domain'].append(('owner_id', '=', self.infosync_user_id))

        # print 'aaaaaaaaaaaaaaaaaaaaaaaaaaactiiiiiiiiiiiioooooooooooooooooooooon', action
        # return action


