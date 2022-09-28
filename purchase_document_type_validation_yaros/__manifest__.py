# -*- coding: utf-8 -*-

{
    'name': 'Que su referencia del proveedor sea estructurada',
    'version': '13.0.1.1.0',
    'author': 'Yaroslab',
    'website': 'http://www.yaroslab.com',
    'description': "Este modelo contiene los parametros de validacion para los campos serie y correlativo en las facturas.",
    'depends': ['account'],
    'data': [
        'security/ir.model.access.csv',
        'views/account_move_views.xml',
        'views/base_views.xml'
    ],
    'installable': True,
    'auto_install': False
}
