{
    'name': 'Non Standard Orders',
    'version': '14.0.0',
    'summary': 'Used to create a non standard foam',
    'sequence': 15,
    'description': "",
    'category': 'Tools',
    'depends': [
        'sale_management',
        'mrp'
    ],
    'data': [
        'views/form.xml',
        'security/ir.model.access.csv',
        # 'views/menus.xml',
        'views/product.xml',
    ],
    # 'data': [
    #     'data/sales_extend.xml'
    # ],
    'installable': True,
    'application': True,
    'auto_install': False,
    #      'assets': { 
    #      'web.assets_backend': [ 
    #          'sales_non_standard/static/src/js/demo.js', 
    #      ] 
    #  } 
    # 'assets': {
    #     'web.assets_backend' [
    #        'sales_non_standard/static/src/js/demo.js',
    #     ],}
}