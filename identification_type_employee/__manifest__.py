# -*- coding: utf-8 -*-
{
    'name': 'Identification type employee',
    'version': '13.0.2.0',
    'author': 'Yaroslab',
    'website': 'http://www.yaroslab.com',
    'description': """
Este modulo crea en empleados un campo llamado Tipo de Documento el cual le permite identificar el tipo de documento que le corresponde a sus empleados,
tambien se utiliza para poder generar varios reportes como Plame, AFP, Boletas etc.

Crea un campo llamado Nacionalidad, que ayuda a identificar a que pais pertenece el tipo de documento.
    """,
    'depends': [
        'hr',
        'l10n_pe_catalog_yaros'
    ],
    'data': ['views/hr_views.xml'],
    'installable': True,
    'auto_install': False,
}
