# -*- coding: utf-8 -*-
{
    'name': "linkaform_licenses",

    'summary': """
        Linkaform Licencias""",

    'description': """
        Administrar las licencias de linkaform directamente desde odoo, esto incluye el crear nuevas licencias, extender periodos y borrar licencias, tambien asignarlas a usuarios de linkaform, para el uso de la plataforma
    """,

    'author': "Erick Hillo",
    'website': "http://www.linkaform.com",
    'category': 'Licenses',
    'version': '0.1',

    'depends': ['base'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/licenses_menu.xml',
    ],
    'installable': True,
}