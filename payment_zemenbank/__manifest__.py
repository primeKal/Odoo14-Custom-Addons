# -*- coding: utf-8 -*-

{
    'name': 'Zemenbank Payment Integration',
    'category': 'Accounting/Payment Acquirers',
    'summary': 'Payment Acquirer: Zemen Implementation',
    'version': '1.0',
    'description': """Zemen Payment Acquirer""",
    'depends': ['payment'],
    'data': [
        'views/payment_views.xml',
        'views/payment_zemen_templates.xml',
        'data/payment_acquirer_data.xml',
    ],
    'installable': True,
    'auto_install': True,
    'post_init_hook': 'create_missing_journal_for_acquirers',
    'uninstall_hook': 'uninstall_hook',
    'license': 'LGPL-3',
}
