{
    'name': 'Sync Comisiones de AFP',
    'version': '13.0.1.0.1',
    'author': 'Ganemo/Yaroslab',
    'website': 'https://www.yaroslab.com',
    'summary': 'Realiza la búsqueda mensual de los diferentes tipos de porcentaje de la AFP',
    'description': '''
    Permite mantener actualizados los diferentes tipos de comisiones de las AFP y el monto máximo de afp para el cálculo de la nómina..
    ''',
    'category': 'Payroll',
    'depends': ['account', 'types_system_pension'],
    'data': ['data/ir_cron.xml',
             'views/pension_system_view.xml',
             ],
    'installable': True,
    'auto_install': False,
}
