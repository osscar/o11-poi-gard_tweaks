# -*- coding: utf-8 -*-
{
    'name': 'GARD Google Maps Tweaks',
    'version': '11.0.1.0.1',
    'author': 'squid',
    'license': 'AGPL-3',
    'category': 'Hidden',
    'description': """
Partner Area
============
""",
    'depends': [
        'contacts',
        'web_google_maps',
        'web_google_maps_drawing',
    ],
    'website': '',
    'data': [
        'security/ir.model.access.csv',
        'views/res_partner_view.xml',
        'views/res_partner_area_view.xml'
    ],
    'demo': [],
    'installable': True
}
