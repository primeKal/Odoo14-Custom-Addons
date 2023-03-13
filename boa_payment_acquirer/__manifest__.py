# -*- coding: utf-8 -*-
# Developed by Kaleb Teshale
# BOA payment Integration to Payment Agrigator Backend
# Kaleb Teshale Feb 09/2023

# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'BOA Payment Integration',
    'version': '13.0.1',
    'summary': 'Tool used to pay to redirect to th BOA payment server and process trnasactions',
    'sequence': 15,
    'description': '',
    'category': 'Tools',
    'depends': [
        'payment'
    ],
    'data': [
        'views/form_boa.xml',
        'views/template.xml',
        # 'data/data.xml'
    ],
    'license' : 'LGPL-3',
    'installable': True,
    'application': True,
    'auto_install': False,
}
