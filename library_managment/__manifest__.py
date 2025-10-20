# -*- coding: utf-8 -*-
{
    'name': "library_managment",

    'summary': "custome module for library managment odoo17",

    'description': """
custome module for library managment
    """,

    'author': "Eman Shalaby",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '17.0.0.0',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/groups.xml',
        'views/library_book.xml',
        'views/library_rental.xml',
        'views/rental_line.xml',
        'views/library_author.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

