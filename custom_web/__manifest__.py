# -*- coding: utf-8 -*-
{
    'name': 'custom_web1',
    # 'version': '15.0.2.1.0',
    'summary': '',
    'sequence': 100,
    'description': "",
    'author': 'Mes',
    'license': 'AGPL-3',
    'depends': [
        'base',
        'website',
        'mail',
        'auth_signup',
    ],
 
    'data': [
        # 'security/ir.model.access.csv',
        'views/view.xml',

        'views/template.xml',
        # 'views/resource.xml',
        'views/mentroship_template.xml',
    ],
    'demo': [],

    'assets': {
        'web.assets_frontend': [
            'custom_web/static/src/css/customstyle.css',
            'custom_web/static/src/js/custom.js',
            'member_dashboard/static/src/js/custom.js',
    ]},
   
    'css': ['member_dashboard/static/src/css/customstyle.css'],
    'qweb': [],
    'images': [],
    'installable': True,
    'application': True,
    'auto_install': False,
  
    
}
