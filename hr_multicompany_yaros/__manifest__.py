{
    "name": u"HR Base Multicompany",
    'version': '13.0.1.0',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    'description': "Módulo base que arregla campos y vistas de modelos HR con el fin de que tengan soporte multicompañia.",
    "depends": [
        'hr_attendance',
        'hr_holidays'
    ],
    "data": ['data/security.xml'],
    'installable': True,
    'auto_install': False,
}
