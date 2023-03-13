# -*- coding: utf-8 -*-
# Developed by Kaleb Teshale
# Chapa Payment integration to the chapa payment API
# Kaleb Teshale Nov 09/2022

# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Payment Agrigator For Ethiopia',
    'version': '13.0.1',
    'summary': 'Tool used to aggrigate all payment methods in ethiopia to odoo',
    'sequence': 15,
    'description': '',
    'category': 'Tools',
    'depends': [
        'payment'
    ],
    'data': [
        'views/agri.xml',
        'security/ir.model.access.csv',
        'views/zemen_template.xml',
        'views/tranc.xml',
    ],
    'images': [
    ],
    'license' : 'LGPL-3',
    'installable': True,
    'application': True,
    'auto_install': False,
}
