# See LICENSE file for full copyright and licensing details.

{
    'name': 'GARD Web Digital Signature',
    'version': '11.0.1.1.0',
    'author': 'squid',
    'complexity': 'easy',
    'depends': [
        'web_digital_sign',
        'stock'],
    "license": "AGPL-3",
    'category': 'Tools',
    'description': '''
     GARD customizations for digital signature.
    ''',
    'summary': '''
        Customized digital signing for GARD.
    ''',
    'data': [
        'views/stock_picking_view.xml'],
    'installable': True,
    'auto_install': False,
}
