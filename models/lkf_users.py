# -*- coding: utf-8 -*-
import requests, simplejson, json, socket, uuid
import  datetime
from dateutil.relativedelta import relativedelta

from pyfcm import FCMNotification

from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo import models, fields, api
from ast import literal_eval
from odoo import exceptions

enviroment = 'test'

if socket.gethostname() == 'odoo-prod':
  enviroment = 'prod'

class Lkf_Users(models.Model):
    _name = 'lkf.users'

    lang  = fields.Char()
    name = fields.Char()
    parent_id = fields.Char() #Many2one(comodel_name='res.partner')
    created_at = fields.Date()
    email = fields.Char()
    phone = fields.Char()
    profile_picture = fields.Char()
    last_login = fields.Date()
    timezone = fields.Char()
    position = fields.Char()
    last_logout = fields.Date()
    deleted_at = fields.Date()
    # id = fields.Integer()
    date_joined = fields.Char()
    id_lkf = fields.Integer()

    def cron_users(self,env):
        ambiente = self.env['lkf.licenses.config'].search([('enviroment', '=', env)])
        host = ambiente.host
        aut = ambiente.api_key
        self.create_in_database(aut,host)


    @api.model
    def create_in_database(self,aut, host):
        query = 'delete from lkf_users'
        self.env.cr.execute(query)
        res = self.connect_to_service(aut,host)
        for item in res:
            id_lkf=item['id']
            name=item['first_name']
            email=item['email']
            phone=item['phone']
            parent_id=item['parent_id']
            created_at=item['created_at']
            position=item['position']
            last_login=item['last_login']
            last_logout=item['last_logout']
            deleted_at=item['deleted_at']
            timezone=item['timezone']
            date_joined= item['date_joined']
            lang=item['lang']
            profile_picture=item['profile_picture']
            query = self.env.cr.execute("""INSERT INTO lkf_users (id,name,email,phone,parent_id,created_at,position,last_login,last_logout,deleted_at,timezone,date_joined,lang,profile_picture )VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""", (id_lkf,name,email,phone,parent_id,created_at,position,last_login,last_logout,deleted_at,timezone,date_joined,lang,profile_picture))

        return True

    def connect_to_service(self, aut, host):
        url = host+'get_lkf_users'
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

    @api.multi
    def restore_pasword(self):
        ambiente = self.env['lkf.licenses.config'].search([('enviroment', '=', enviroment)])
        url = ambiente.host+'set_user_password'
        headers = {'Content-type': 'application/json','Authorization': ambiente.api_key}
        password = self.env['lkf.infiltration'].search([('user_id', '=', self.id)])[-1].password_old
        objeto = {
                    "user_id": self.id,
                    "new_pass": password
                }
        r = requests.post(url,simplejson.dumps(objeto),headers=headers)

        if r.status_code == 200:
            raise exceptions.Warning("Password Restaurado")
            return True
        else :
            return False

    @api.multi
    def change_fake_pasword(self):
        get_pass = self.get_user_password()
        if get_pass == True:
            set_pass = self.set_fake_password()
            raise exceptions.Warning("Contraseña Fake actualizada correctamente")

    @api.multi
    def set_fake_password(self):
        ambiente = self.env['lkf.licenses.config'].search([('enviroment', '=', enviroment)])
        url = ambiente.host+'set_temp_password'
        headers = {'Content-type': 'application/json','Authorization': ambiente.api_key}
        objeto = {"user_id": self.id}

        r = requests.post(url,simplejson.dumps(objeto),headers=headers)

        if r.status_code == 200:
            return True
        else :
            return False

    @api.multi
    def get_user_password(self):
        ambiente = self.env['lkf.licenses.config'].search([('enviroment', '=', enviroment)])
        url = ambiente.host+'get_user_pass?user_id='+str(self.id)
        headers = {'Content-type': 'application/json','Authorization': ambiente.api_key}
        response = {'data':{}, 'status_code':''}
        res = ""

        r = requests.get(url,headers=headers)
        response['status_code'] = r.status_code
        if r.status_code == 200:
            r_data = simplejson.loads(r.content)
            if 'response' in r_data.keys():
                response['data'] = r_data['response']
                values ={
                    "user_id": self.id,
                    "email": self.email,
                    "password_old": response['data']['response']
                }
                res = self.env['lkf.infiltration'].create(values)
                return True
            else:
                response['data'] = r_data
                return False

    @api.multi
    def delete_api_key(self):
        ambiente = self.env['lkf.licenses.config'].search([('enviroment', '=', enviroment)])
        url = ambiente.host+'delete_api_key'
        headers = {'Content-type': 'application/json','Authorization': ambiente.api_key}
        objeto = {"user_id": self.id}

        r = requests.post(url,simplejson.dumps(objeto),headers=headers)

        if r.status_code == 200:
            raise exceptions.Warning('ApiKey Borrada exitosamente')
            return True
        else :
            return False

    @api.multi
    def get_lkf_login(self):
        ambiente = self.env['lkf.licenses.config'].search([('enviroment', '=', enviroment)])
        url = ambiente.host+'get_login?user_id='+str(self.id)
        headers = {'Content-type': 'application/json','Authorization': ambiente.api_key}
        response = {'data':{}, 'status_code':''}
        res = ""

        r = requests.get(url,headers=headers)
        response['status_code'] = r.status_code
        if r.status_code == 200:
            r_data = simplejson.loads(r.content)
            if 'response' in r_data.keys():
                response['data'] = r_data['response']
                mensaje = "API KEY:  " + str(response['data']['response'])
                raise exceptions.Warning(mensaje)
                return True
            else:
                response['data'] = r_data
                return False

    @api.multi
    def get_message_id(self):
        return uuid.uuid4().hex

    @api.multi
    def get_firebase_token(self,user_id):
        ambiente = self.env['lkf.licenses.config'].search([('enviroment', '=', enviroment)])
        url = ambiente.host+'get_firebase_token?user_id='+str(user_id)
        headers = {'Content-type': 'application/json','Authorization': ambiente.api_key}
        response = {'data':{}, 'status_code':''}

        r = requests.get(url,headers=headers)
        response['status_code'] = r.status_code
        if r.status_code == 200:
            r_data = simplejson.loads(r.content)
            if 'response' in r_data.keys():
                response['data'] = r_data['response']
                if 'No Firebase Token found' in response['data']:
                    return response['data']['response']
                else:
                    raise exceptions.Warning('No existe el Firebase Token')
                    return False

    @api.multi
    def send_push_logout(self):
        apikey = self.env['lkf.licenses.config'].search([('enviroment', '=', 'app')])
        push_service = FCMNotification(api_key=apikey.api_key)
        registration_id = self.get_firebase_token(self.id)
        message_id = self.get_message_id()
        data_message={
            'action': 'logout',
             'message_id': message_id,
             'notification': {'body': 'Logout, someone else is using you account in another device.',
              'date': 0,
              'from': {'email': 'donotreply@linkaform.com',
               'id': 126,
               'name': 'Soporte Linkaform'},
              'title': 'Logout',
              'to': {'email': self.email,
               'id': 1773,
               'name': self.name}},
             'object': {}
            }
        result = push_service.notify_single_device(registration_id=registration_id, data_message=data_message )

class lkf_licenses_config(models.Model):
    _name = "lkf.licenses.config"

    enviroment = fields.Char()
    host = fields.Char()
    api_key = fields.Char()

class linkaform_infiltration(models.Model):
    _name = 'lkf.infiltration'

    user_id = fields.Integer()
    email = fields.Char()
    password_old = fields.Char()

