# -*- coding: utf-8 -*-
from odoo import http

# class LinkaformLicenses(http.Controller):
#     @http.route('/linkaform_licenses/linkaform_licenses/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/linkaform_licenses/linkaform_licenses/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('linkaform_licenses.listing', {
#             'root': '/linkaform_licenses/linkaform_licenses',
#             'objects': http.request.env['linkaform_licenses.linkaform_licenses'].search([]),
#         })

#     @http.route('/linkaform_licenses/linkaform_licenses/objects/<model("linkaform_licenses.linkaform_licenses"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('linkaform_licenses.object', {
#             'object': obj
#         })