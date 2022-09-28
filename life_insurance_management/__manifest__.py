# -*- coding: utf-8 -*-
{
    'name': 'Life insurance management',
    'version': '13.0.1.1.0',
    'author': 'Yaroslab',
    'website': 'http://www.yaroslab.com',
    'description': """
Este modulo crea un módelo en el módulo de localización menu Datos de nómina donde puedes administrar las 
pólizas de seguro de vida de los trabajadores.
    """,
    'depends': [
        'localization_menu',
        'hr'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_views.xml',
        'views/life_insurance_views.xml'
    ],
    'installable': True,
    'auto_install': False,
}
