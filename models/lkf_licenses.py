# -*- coding: utf-8 -*-
import requests, simplejson, json, socket
import  datetime
from dateutil.relativedelta import relativedelta

from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo import models, fields, api
from ast import literal_eval

enviroment = 'test'

if socket.gethostname() == 'odoo-prod':
  enviroment = 'prod'


class linkaform_licenses(models.Model):
    _name = 'lkf.licenses'

    owner_id = fields.Many2one(comodel_name='lkf.users', string='Owner')
    user_id = fields.Many2one(comodel_name='lkf.users', string='User',  domain= lambda self:self._get_users())
    user_email = fields.Char()  #(compute='_set_user_email')
    user_name = fields.Char()  #(compute='_set_user_name')
    connection_name = fields.Many2one(comodel_name='lkf.users', string='Connection Name') #compute='_set_connection'
    token = fields.Char()
    expiration = fields.Date()
    is_active = fields.Boolean(default=True)
    plan_id = fields.Char()
    product_id = fields.Many2one(comodel_name="product.product")
    subscription_id = fields.Integer()
    update_at = fields.Date()
    properties  = fields.Text()
    number = fields.Integer(string="N° de Licencias")

    @api.model
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
    def cron_licenses(self,env):
        ambiente = self.env['lkf.licenses.config'].search([('enviroment', '=', env)])
        host = ambiente.host
        aut = ambiente.api_key
        self.create_in_database(aut,host)

    @api.model
    def create_in_database(self,aut,host):
        query = 'delete from lkf_licenses'
        self.env.cr.execute(query)
        res = self.connect_to_service(aut,host)
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

            licenses = self.env.cr.execute("""INSERT INTO lkf_licenses (owner_id,user_id,user_email,user_name,connection_name,token,expiration,is_active,plan_id,product_id,subscription_id,update_at,properties) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",(owner_id,user_id,user_email,user_name,connection_id,token,expiration,is_active,plan_id,product_id,subscription_id,update_at,properties))


        return True

    def connect_to_service(self,aut,host):
        url = host+'get_account_license'
        headers = {'Content-type': 'application/json','Authorization': aut}
        response = {'data':{}, 'status_code':''}

        r = requests.get(url,headers=headers)
        response['status_code'] = r.status_code

        if r.status_code == 200:
            r_data = simplejson.loads(r.content)
            if 'objects' in r_data.keys():
                response['data'] = r_data['objects']
            else:
                response['data'] = r_data
        return response['data']['response']['response']


    @api.model
    def create(self,values):
        ambiente = self.env['lkf.licenses.config'].search([('enviroment', '=', enviroment)])
        url = ambiente.host+'create_license'
        headers = {'Content-type': 'application/json','Authorization': ambiente.api_key}
        response = {'data':{}, 'status_code':''}
        objeto = {
                "account_id": values['owner_id'],
                "product_id":values['product_id'],
                "expiration": values['expiration']
            }


        if values['connection_name']:
            objeto["connection_id"] = values['connection_name']
        if values['user_id']:
            objeto['user_id'] = values['user_id']
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
        ambiente = self.env['lkf.licenses.config'].search([('enviroment', '=', enviroment)])
        url = ambiente.host+'update_license'
        headers = {'Content-type': 'application/json','Authorization': ambiente.api_key}
        lic = self.search([('id','=',self.id)])
        data = {'license_token':lic.token, 'update_by':['token']}

        if 'owner_id'  in values.keys():
            data['account_id'] = values['owner_id']

        if 'expiration' in values.keys():
            data['expiration'] = values['expiration']

        if 'connection_id' in values.keys():
            data['connection_id'] = values['connection_id']

        if 'user_id' in values.keys():
            data['user_id'] = values['user_id']

        if 'product_id' in values.keys():
            data['product_id'] = values['product_id']

        if 'properties' in values.keys():
            data['properties'] = values['properties']

        values['update_at'] = datetime.datetime.now().strftime("%Y-%m-%d")

        r = requests.patch(url,simplejson.dumps(data),headers=headers)

        res = super(linkaform_licenses,self).write(values)




class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.multi
    def acction_view_licenses(self):
        self.ensure_one()
        action = self.env.ref('linkaform_licenses.action_license_tree').read()[0]
        action['domain'] = literal_eval(action['domain'])
        action['domain'].pop(0)
        action['domain'].append(('|'))
        action['domain'].append(('owner_id', '=', self.infosync_user_id ))
        action['domain'].append(('user_id', '=', self.infosync_user_id ))
        action['domain'].append(('is_active', '=' , True))

        return action

class linkaform_licenses_custom(models.TransientModel):
    _name = 'lkf.licenses_update'

    expiration = fields.Date(string="Fecha de Expiracion de Licencias")
    @api.multi
    def update_liceneses(self):
        for records in self:
            print('recors', dir(records))



