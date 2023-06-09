{
    'name': 'Graph Api',
    'category': 'Website/Website',
    'summary': 'Build custom web forms',
    'description': """
        Customize and create your own web forms.
        This module adds a new building block in the website builder in order to build new forms from scratch in any website page.
    """,
    'version': '1.0',
    'depends': ['base','website'],
    'data': [
        'views/custom_snippet.xml',
        'views/custom_template.xml',
        'views/assets.xml',
        'views/ir_models_view.xml',
        'views/options.xml',

        'security/ir.model.access.csv',
        # 'static/src/xml/param_template.xml'
    ],
    'xmlDependencies': ['static/src/xml/param_template.xml'],
    # 'qweb': [
    #     'static/src/xml/param_template.xml',],
    'installable': True,
    'auto_install': True,
    'license': 'LGPL-3',
}
