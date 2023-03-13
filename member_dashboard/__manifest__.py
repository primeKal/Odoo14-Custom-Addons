
{
    'name': 'Membership Dashboard',
    'version': '1.0',
    'category': 'Extra-tools',
    'description': "",
    "author": " ",
    'depends': ['base','account', 'web', 'project','portal'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/membership_data.xml',
        'views/membership_template.xml',
        'views/complaint_form_views.xml',
        'views/compliant_list.xml',
        # 'views/assets.xml',
        'views/mapping.xml',
        'views/res.partner.extend.xml'
    ],
    #      'assets': {
    #     'web.assets_frontend': [
    #         'member_dashboard/static/src/js/custom.js',
    #         '/member_dashboard/static/src/js/vendor.bundle.base.js',
    #         '/member_dashboard/static/src/js/Chart.min.js',
    # ]},

    'css': ['static/src/css/customstyle.css'],
    'license': 'LGPL-3',
    'installable': True,
    'application': True,
    'auto_install': False,
}
