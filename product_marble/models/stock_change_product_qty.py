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

from openerp.osv import fields, osv
import _common as comm
from openerp.tools.translate import _
from openerp import tools

import logging
_logger = logging.getLogger(__name__)

class stock_change_product_qty(osv.osv_memory):
    _name = "stock.change.product.qty"
    _inherit = "stock.change.product.qty"
    _description = "Change Product Quantity"

    def onchange_calculate_dim(self, cr, uid, ids, dim_id, dim_qty, is_raw):
        dim_qty = 1 if dim_id and not dim_qty else dim_qty
        val = {
            'dimension_qty' : dim_qty,
            'new_quantity'  : self.calculate_dim(cr, uid, dim_id, dim_qty, is_raw)
        }
        # _logger.info(">> onchange_calculate_dim >> 1- val = %s", val)
        return {'value': val}


    def calculate_dim(self, cr, uid, dim_id, dim_qty, is_raw):
        if not is_raw or not dim_id:
            return 0.00

        obj  = self.pool.get('product.marble.dimension')
        data = obj.read(cr, uid, [dim_id], ['m2'], context=None)
        m2   = data[0]['m2'] if (len(data) > 0 and len(data[0]) > 0) else 0.00

        pro_qty = dim_qty * m2
        return pro_qty

    # el dominio de dimensiones permitidas a inventariar (agregar o quitar
    # unidades de placas o recortes o marmetas) lo define el model Balance.
    #
    # Al inventariar, no puedo poner ni sacar unidades para Dimensiones
    # inexistentes, sin registrar en Balance.
    # ¿Como voy actualizar algo que no existe en Balance?
    def _get_dimensions_domain(self, cr, uid, pid, context=None):
        return []

        bal = self.pool.get('product.marble.dimension.balance')
        bal_ids = bal.search(cr, uid, [('product_id','=',pid)], context=context)
        dim_ids = [b.dimension_id.id for b in bal.browse(cr, uid, bal_ids)]
        dom = [('id', 'in', dim_ids)]

        # _logger.info(">> _get_dimensions_domain >> 5- dom = %s", dom)
        return dom

    _columns = {
        'domain_dimension_ids': fields.function(_get_dimensions_domain, type='char', size=255, method=True, string='Domain Dimension IDs'),
        # 'dimension_id': fields.many2one('product.marble.dimension', 'Dimension'),
        'dimension_id': fields.many2one('product.marble.dimension', 'Dimension', domain="[('state','=','done')]"),
        'dimension_qty': fields.integer('Units', size=3),
        'product_uom': fields.many2one('product.uom', 'Unit of Measure', readonly=True),
        'is_raw': fields.boolean('Is Raw Material'),
    }

    def default_get(self, cr, uid, fields, context):
        res = super(stock_change_product_qty, self).default_get(cr, uid, fields, context=context)

        res['domain_dimension_ids'] = []
        res['dimension_id'] = 0
        res['dimension_qty'] = 0
        res['new_quantity'] = 0
        res['is_raw'] = False

        pid = res['product_id']
        if not pid:
            return res

        prod = self.pool.get('product.product').browse(cr, uid, [pid], context=context)
        res['is_raw'] = prod.is_raw
        res['product_uom'] = prod.uom_id.id
        # res['domain_dimension_ids'] = self._get_dimensions_domain(cr, uid, pid)

        # _logger.info(">> idefault_get >> 3 >> res = %s", res)
        return res


    def create(self, cr, uid, data, context=None):
        if data.get('is_raw',False):
            qty_m2 = self.calculate_dim(cr, uid, data['dimension_id'], data['dimension_qty'], data['is_raw'])
            data['new_quantity'] = qty_m2

        return super(stock_change_product_qty, self).create(cr, uid, data, context=context)


    # overwrite: stock > stock_inventory_line - odoo v8.0 - line: 75 - 114
    # sobre escribo metodo para incorporar 'dimensiones' en caso de ser materia prima
    def change_product_qty(self, cr, uid, ids, context=None):
        """ Changes the Product Quantity by making a Physical Inventory.
        @param self: The object pointer.
        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param ids: List of IDs selected
        @param context: A standard dictionary
        @return:
        """
        if context is None:
            context = {}

        inventory_obj = self.pool.get('stock.inventory')
        inventory_line_obj = self.pool.get('stock.inventory.line')

        for data in self.browse(cr, uid, ids, context=context):
            if data.new_quantity < 0:
                raise osv.except_osv(_('Warning!'), _('Quantity cannot be negative.'))

            ctx = context.copy()
            ctx['location'] = data.location_id.id
            ctx['lot_id'] = data.lot_id.id
            inventory_id = inventory_obj.create(cr, uid, {
                'name': _('INV: %s') % tools.ustr(data.product_id.name),
                'product_id': data.product_id.id,
                'location_id': data.location_id.id,
                'lot_id': data.lot_id.id}, context=context)

            product = data.product_id.with_context(location=data.location_id.id)
            th_qty = product.qty_available

            bal = self.pool.get('product.marble.dimension.balance')
            th_qty_dim = bal.unit_qty_available(cr, uid, data.product_id.id, data.dimension_id.id, context)
            _logger.info(">> change_product_qty >> 1- th_qty_dim = %s", th_qty_dim)

            line_data = {
                'inventory_id': inventory_id,
                'product_qty': data.new_quantity,
                'location_id': data.location_id.id,
                'product_id': data.product_id.id,
                'product_uom_id': data.product_id.uom_id.id,
                'theoretical_qty': th_qty,
                'prod_lot_id': data.lot_id.id,

                # add dimension data...
                'dimension_id': data.dimension_id.id,
                'theoretical_dimension_qty': th_qty_dim,  # old qty value (existing units registered [x system])
                'dimension_qty': data.dimension_qty,    # new qty value (existing units physically [manual adjustment])
            }
            inventory_line_obj.create(cr, uid, line_data, context=context)
            inventory_obj.action_done(cr, uid, [inventory_id], context=context)
        return {}

stock_change_product_qty()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
