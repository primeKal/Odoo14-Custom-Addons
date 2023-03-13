{
    'name': 'Production Incentive',
    'version': '14.0.0',
    'summary': 'give production incentive',
    'sequence': 15,
    'description': "",
    'category': 'Tools',
    'depends': [
        'mrp',
        'hr',
    ],
    'data': [
        'views/form.xml',
        'views/res_config_settings_views.xml',
        'security/ir.model.access.csv',
        'views/model.xml'
    ],
    # 'data': [
    #     'data/sales_extend.xml'
    # ],
    'installable': True,
    'application': True,
    'auto_install': False,
}