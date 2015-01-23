# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name'       : 'Marble Works',
    'version'    : '1.0',
    'author'     : 'Antares Consulting',
    'description': 'Definicion de Productos para Marmoleria.',
    'category'   : 'Product Marble',
    'website'    : 'http://www.antaresconsulting.com.ar',
    'depends'    :[
            'web',
            'stock',
            'sale',
            'purchase',
            'hr',
    ],
    'data'       :[
        'security/groups_security.xml',
        'security/ir.model.access.csv',

        'data/heavy_data.xml',
        'data/users_data.xml',
        'data/marble_data.xml',

        'views/marble_login_view.xml',
        'views/product_dimension_view.xml',
        'views/product_view.xml',
        #'views/res_partner_view.xml',
        'views/stock_view.xml',
        'views/stock_change_product_qty_view.xml',

        'views/marble_actions.xml',
        'views/marble_menu.xml',

    ],
    'css': [
        'static/src/css/style.css',
    ],
    'auto_install':False,
    'installable': True,
    'active'     : True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
