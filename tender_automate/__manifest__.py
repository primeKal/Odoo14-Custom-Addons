{
    'name': 'Auto Ananlyze Tender',
    'version': '14.0.0',
    'summary': 'Auto analyzes the purchase agrements',
    'sequence': 15,
    'description': "",
    'category': 'Tools',
    'depends': [
        'purchase',
        'crm'
    ],
    'data': [
        'views/form.xml',
    ],
    # 'data': [
    #     'data/sales_extend.xml'
    # ],
    'installable': True,
    'application': True,
    'auto_install': False,
}