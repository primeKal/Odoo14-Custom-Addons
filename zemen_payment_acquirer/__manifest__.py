# -*- coding: utf-8 -*-
# Developed by Kaleb Teshale
# Zemen Payment integration to local payment server
# Kaleb Teshale Nov 09/2022

# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Zemen Payment Integration',
    'version': '13.0.1',
    'summary': 'Tool used to pay to redirect to the zemen payment server and process trnasactions',
    'sequence': 15,
    'description': 'Tool used to pay to redirect to the zemen payment server and process transaction.Can be used from website'
                   'and from the sales(by generating a payment link',
    'category': 'Tools',
    'depends': [
        'payment'
    ],
    'data': [
        'views/form_chapa.xml',
        'views/template.xml',
        'data/data.xml'
    ],
    'license' : 'LGPL-3',
    'installable': True,
    'application': True,
    'auto_install': False,
}
