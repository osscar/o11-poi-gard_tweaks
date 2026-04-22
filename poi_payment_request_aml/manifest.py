{
    'name': 'Payment Request AML Relation',
    'version': '11.0.1.0.0',
    'category': 'Accounting',
    'author': 'squid',
    'depends': ['poi_payment_request', 'account'], # Depends on your base request module
    'data': [
        'views/account_move_line_view.xml',
        'views/account_payment_request_view.xml',
    ],
    'installable': True,
}