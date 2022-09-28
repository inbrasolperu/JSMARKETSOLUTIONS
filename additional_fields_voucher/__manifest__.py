{
    'name': 'Additional fields voucher',
    'version': '13.0.1.0.0',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    'description': """
Este modulo se encarga de crear varios campos necesarios para los voucher, constancias y contrato. Instala el campo 
de Firma del empleador para poder importar una firma digital.
""",
    'depends': ['hr_payroll'],
    'data': [
        'views/hr_views.xml'
    ],
    'installable': True,
    'auto_install': False,
}
