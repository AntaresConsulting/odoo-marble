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
#    GNU Affero GeneralGeneral Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import osv
from openerp.osv import fields
from openerp.tools.translate import _
from operator import itemgetter

import logging
_logger = logging.getLogger(__name__)

# import pdb
# pdb.set_trace()

class product_marble_dimension_balance(osv.osv):

    _name = 'product.marble.dimension.balance'
    _description = "Balance between Marble - Dimension"

    def register_balance000(self, cr, uid,data,context=None):
        prod_id = data.get('prod_id')
        dimension_id = data.get('dim_id')
        dimension_qty = data.get('dimension_qty')
        typeMove = data.get('typeMove')

        balance_obj = self.pool.get('product.marble.dimension.balance')
        bal_ids = balance_obj.search(cr,uid,[('dimension_id','=',dimension_id),('marble_id','=',prod_id)])

        if not bal_ids:
            balance_obj.create(cr,uid,{'dimension_id':dimension_id,'marble_id':prod_id,'qty_m2':0,'qty_unit':dimension_qty})
            if typeMove == 'in':
                qval = dimension_qty+dimension_qty
                balance_obj.write(cr,uid,bal_ids,{'qty_m2':0,'qty_unit':qval})
            if typeMove == 'out':
                qval = dimension_qty-dimension_qty
                balance_obj.write(cr,uid,bal_ids,{'qty_m2':0,'qty_unit':qval})
        else:
            qty_bal = balance_obj.read(cr,uid,bal_ids,['qty_unit'])
            if typeMove == 'in':
                qval = qty_bal[0]['qty_unit']+dimension_qty
                balance_obj.write(cr,uid,bal_ids,{'qty_m2':0,'qty_unit':qval})
            if typeMove == 'out':
                qval = qty_bal[0]['qty_unit']-dimension_qty
                balance_obj.write(cr,uid,bal_ids,{'qty_m2':0,'qty_unit':qval})
        return 1

    # refactory sources...
    def register_balance(self, cr, uid, data, context=None):
        pro_id = data.get('prod_id', 0)
        dim_id = data.get('dim_id', 0)
        dim_qty = data.get('dimension_qty', 0.00)
        dim_m2 = data.get('dimension_m2', 0)
        tyMove = data.get('typeMove', '')

        bid = self.search(cr,uid,[('dimension_id','=',dim_id),('marble_id','=',pro_id)])
        if bid:
            # Update...
            bal = self.read(cr, uid, bid, ['qty_unit', 'qty_m2'])[0]
            if tyMove == 'in':
                dim_qty = bal['qty_unit'] + dim_qty
                dim_m2 = bal['qty_m2'] + dim_m2

            elif tyMove == 'out':
                dim_qty = bal['qty_unit'] - dim_qty
                dim_m2 = bal['qty_m2'] - dim_m2
            #
            self.write(cr, uid, bid, {'qty_unit':dim_qty, 'qty_m2':dim_m2})
        else:
            # New...
            if tyMove == 'out':
                dim_qty *= -1
                dim_m2 *= -1
            #
            self.create(cr, uid, {'dimension_id':dim_id, 'marble_id':pro_id, 'qty_unit':dim_qty, 'qty_m2':dim_m2})
        return 1

    _columns = {
        'marble_id': fields.many2one('product.product', 'Product Marble ID', select=True, readonly=True),
        'dimension_id': fields.many2one('product.marble.dimension', 'Product Marble Dimension ID', select=True, readonly=True),

        'qty_unit': fields.float('Qty Unit', type="integer", readonly=True),
        'qty_m2': fields.float('Qty M2', digits=(5, 2), type="float", readonly=True),
    }

    _defaults = {
        'qty_unit': lambda *a: 0.00,
        'qty_m2': lambda *a: 0.00,
    }

    _sql_constraints = [
        ('unique_marble_dim', 'unique(marble_id, dimension_id)', 'The record already exists.')
    ]


product_marble_dimension_balance()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
