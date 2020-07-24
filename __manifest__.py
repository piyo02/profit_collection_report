{
    'name': 'Profit Collection Report',
    'category': 'hidden',
    'version': '10.0',
    'summary': 'Addon for Print Profit Collection Report.',
    'description': '''Get Margin from invoice and print it in Profit Collection Report'''
                   ,
    'depends': ['base', 'account'],
    'data': [
        'report/account_report.xml',
        'report/account_temp.xml',
        'wizard/profit_wizard.xml'
    ],
    'images': [''],
    'auto_install': False,
    'installable': True,
    'application': False,
}
