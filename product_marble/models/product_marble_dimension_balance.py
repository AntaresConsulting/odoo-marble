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

    # retorno registro unico o False...
    def get(self, cr, uid, pro_id, dim_id, context=None):
        ids = self.search(cr, uid, [('product_id','=',pro_id),('dimension_id','=',dim_id)], context=context)
        for bal in self.browse(cr, uid, ids):
            return bal
        return False

#    def qty_m2_available(self, cr, uid, pro_id, dim_id, context=None):
#        bal_ids = self.search(cr, uid, [('product_id','=',pro_id),('dimension_id','=',dim_id)], context=context)
#        for bal in self.browse(cr, uid, bal_ids):
#            return bal.qty_unit or 0
#        return 0

    def register_balance(self, cr, uid, data, context=None):
        # _logger.info(">> register_balance >> 1- data = %s", data)

        pro_id = data.get('prod_id', 0)
        dim_id = data.get('dim_id', 0)
        dim_qty = data.get('dimension_qty', 0)
        dim_m2 = data.get('dimension_m2', 0.000)

        tyMove = data.get('typeMove','')
        if (tyMove not in ['in','out']):
            raise osv.except_osv(_('Error!'), _('Type-Move is not [\'in\',\'out\'].'))

        operacion = ' + ' if (tyMove == 'in') else ' - '
        bid = self.search(cr,uid,[('dimension_id','=',dim_id),('product_id','=',pro_id)])
        if bid:
            # Update...
            for bal in self.browse(cr, uid, bid):
                sQty = str(bal.qty_unit) + operacion + str(dim_qty)
                sM2 = str(bal.qty_m2) + operacion + str(dim_m2)
                val = {'qty_unit': eval(sQty), 'qty_m2': eval(sM2)}
                self.write(cr, uid, bid, val)
        else:
            # New...
            sQty = operacion + str(dim_qty)
            sM2 = operacion + str(dim_m2)
            val = {'dimension_id': dim_id, 'product_id': pro_id, 'qty_unit': eval(sQty), 'qty_m2': eval(sM2)}
            self.create(cr, uid, val)

        return True

    _columns = {
        'product_id': fields.many2one('product.product', 'Product Marble ID', select=True, readonly=True),
        'dimension_id': fields.many2one('product.marble.dimension', 'Dimension', select=True, readonly=True),
        'qty_unit': fields.float('Qty Unit', type="integer", readonly=True),
        'qty_m2': fields.float('Qty M2', digits=(5, 3), type="float", readonly=True),
    }

    _defaults = {
        'qty_unit': lambda *a: 0,
        'qty_m2': lambda *a: 0.000,
    }

    _sql_constraints = [
        ('unique_marble_dim', 'unique(product_id, dimension_id)', 'The record already exists.')
    ]

product_marble_dimension_balance()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
