# -*- coding: utf-8 -*-


{
    'name': 'ODOO Manuals',
    'version': '1.0',
    'category': 'Knowledge Management',
    'sequence': 14,
    'summary': '',
    'description': """
    """,
    'author':  'Antares Consulting',
    'website': 'www.antaresconsulting.com.ar',
    'images': [
    ],
    'depends': [
        'document_page',
        'document_url',
        'attachment_preview',
    ],
    'data': [
        'menu_item.xml',
        'page_general.xml',
        'page_stock.xml',
        'page_purchase.xml',
        'page_rh.xml',
    ],
    'demo': [
    ],
    'test': [
    ],
    'installable': True,
    'auto_install': True,
    'application': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
