# -*- coding: utf-8 -*-
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo import models, fields, api
from ast import literal_eval

class linkaform_licenses(models.Model):
    _name = 'lkf.licenses'


    owner_id = fields.Char(string="Owner id")              #Selection(selection_add=[('a', 'A')])
    user_id = fields.Char(string="User id")              #Selection(selection_add=[('a', 'A')])
    token = fields.Char()
    expiration = fields.Date()
    is_active = fields.Boolean()
    plan_id = fields.Integer()
    product_id = fields.Integer()
    subscription_id = fields.Integer()
    connection_id = fields.Integer()
    due_date = fields.Char()
    update_at = fields.Date()
    properties  = fields.Text()


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def acction_view_licenses(self):
        self.ensure_one()
        action = self.env.ref('linkaform_licenses.action_license_tree').read()[0]
        # action['domain'] = literal_eval(action['domain'])
        # action['domain'].append(('partner_id', 'child_of', self.id))
        return action