# See LICENSE file for full copyright and licensing details.

{
    'name': 'GARD Web Digital Signature',
    'version': '11.0.1.0.0',
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
        Touch screen enable so user can add signature with touch devices.
        Digital signature can be very usefull for documents.
    ''',
    'data': [
        'views/stock_picking_view.xml'],
    'installable': True,
    'auto_install': False,
}
