import requests, simplejson, json
import  datetime

from odoo import models, fields, api

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

    @api.model
    def create_in_database(self):
        res = self.connect_to_service()
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

            print '',query
        return True


    def connect_to_service(self):
        url = 'https://zato.linkaform.com/api/126/get_lkf_users'
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