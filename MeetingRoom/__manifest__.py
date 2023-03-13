# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Meeting Room',
    'version': '13.1.1',
    'summary': 'Schedule meetings for your office  meeting room',
    'sequence': 15,
    'description': "Easily book meetings of a certain period for your office meeting room so that other system users can book accordingly",
    'category': 'Tools',
    'depends': [
        'mail'
    ],
    'data': [
        'security/ir.model.access.csv',
        'datas/actions.xml',
        'views/meeting.xml',

    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}


