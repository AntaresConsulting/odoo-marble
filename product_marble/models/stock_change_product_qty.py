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
from openerp import tools, exceptions

import logging
_logger = logging.getLogger(__name__)

class stock_change_product_qty(osv.osv_memory):
    _name = "stock.change.product.qty"
    _inherit = "stock.change.product.qty"
    _description = "Change Product Quantity"

    _columns = {
        'is_raw': fields.boolean('Is Raw Material'),
        'dimension_id': fields.many2one('product.marble.dimension', 'Dimension', domain=[('state','=','done')]),
        'dimension_unit_new': fields.integer('New Qty Units', size=3),   # units
        'dimension_m2_new': fields.float('New Qty M2', digits=(5,3)),  # m2
        'dimension_unit_theoretical': fields.integer('Theoretical Dimension Quantity Units', size=3, readonly=True),  # units
        'dimension_m2_theoretical': fields.float('Theoretical Dimension Quantity M2', digits=(5,3), readonly=True),  # m2
        'product_uom': fields.many2one('product.uom', 'Unit of Measure', readonly=True),
        'dimension_uom_theoretical': fields.many2one('product.uom', 'Theoretical UOM', readonly=True),
    }

    _defaults = {
        'is_raw':                     False,
        'new_quantity':               0.000,
        'dimension_id':               False,
        'dimension_unit_new':         0,
        'dimension_m2_new':           0.000,
        'dimension_unit_theoretical': 0,
        'dimension_m2_theoretical':   0.000,
        'dimension_uom_theoretical':  False,
    }

    def default_get(self, cr, uid, fields, context):
        res = super(stock_change_product_qty, self).default_get(cr, uid, fields, context=context)

        res['is_raw'] =                     False
        res['dimension_id'] =               False
        res['dimension_unit_new'] =         0
        res['dimension_m2_new'] =           0.000
        res['dimension_unit_theoretical'] = 0
        res['dimension_m2_theoretical'] =   0.000
        res['dimension_uom_theoretical'] =  False
        res['new_quantity'] =               0.000

        pid = res.get('product_id',0) or context.get('active_id') or 0
        for prod in self.pool.get('product.product').browse(cr, uid, [pid], context=context):
            #res['is_raw'] = prod.is_raw
            res['is_raw'] = (prod.prod_type == comm.RAW)
            res['product_uom'] = prod.uom_id.id
            res['dimension_uom_theoretical'] = res['product_uom']

        # _logger.info(">> default_get >> 1 >> res = %s", res)
        return res

    def create(self, cr, uid, data, context=None):
        data['product_id'] = context.get('active_id', False)
        res = self.calculate_dim(cr, uid, data, context)

        _logger.info(">> create >> res = %s", res)
        return super(stock_change_product_qty, self).create(cr, uid, res, context=context)

    # valido dimension, que haya sido CONFIRMDA...
    def is_valid_dim(self, cr, uid, dim_id, context=None):
        obj_dim = self.pool.get('product.marble.dimension')
        dim = obj_dim.browse(cr, uid, [dim_id], context=context)
        return (not dim_id) or (dim.id and dim.state == 'done')

    def onchange_calculate_dim(self, cr, uid, ids, pro_id, dim_id, dim_un, context=None):

        if not self.is_valid_dim(cr, uid, dim_id, context):
            msg = "La 'Dimension' seleccionada NO FUE CONFIRMADA.\nFavor de CONFIRMAR la Dimensión para su uso.\nSe cancela la selección."
            res = {
                    'value'   : {'dimension_id' : False},
                    'warning' : {'title' : 'Atención!!!', 'message' : msg}
            }
            #_logger.info(">> res = %s", res)
            return res
        
        val = {
            'product_id':                   pro_id or False,   # requerido
            'dimension_id':                 dim_id or False,   # opcional
            'dimension_unit_new':           dim_un or 0.000,   # opcional

            # datos que se re-calculan...
            'is_raw':                       False,
            'new_quantity':                 0,
            'dimension_m2_new':             0.000,

            'dimension_unit_theoretical':   0,
            'dimension_m2_theoretical':     0.000,

            'product_uom':                  False,
            'dimension_uom_theoretical':    False,
        }
        res = self.calculate_dim(cr, uid, val, context)
        return {'value': res}

    def calculate_dim(self, cr, uid, val, context=None):
        # _logger.info(">> calculate_dim >> 1- val = %s", val)

        pro_id  = val.get('product_id',   False)    # requerido
        dim_id  = val.get('dimension_id', False)    # requerido
        new_qty = val.get('dimension_unit_new', 0)  # requerido

        if not pro_id:
            _logger.warning(">> calculate_dim >> No se puede Calcular Dimension, no existe product_id >> val = %s", val)
            return val

        # misc...
        data = self.pool.get('product.product').browse(cr, uid, [pro_id], context=None)[0]
        #is_raw = data.is_raw
        is_raw = (data.prod_type == comm.RAW)
        uom = data.uom_id.id
        val['is_raw'] = is_raw
        val['product_uom'] = uom

        if not (is_raw and dim_id):
            # _logger.info(">> calculate_dim >> 2- val = %s", val)
            return val

        # calculate dimension: new qty [units + m2]
        data = self.pool.get('product.marble.dimension').browse(cr, uid, [dim_id], context=None)[0]
        m2 = (data and data.m2) or 0.000
        val['dimension_unit_new'] = (dim_id and not new_qty and 1) or (dim_id and new_qty) or 1
        val['dimension_m2_new']   = val['dimension_unit_new'] * m2

        # retrieve balance: available qty [units + m2]
        data = self.pool.get('product.marble.dimension.balance').get(cr, uid, pro_id, dim_id, context)
        val['dimension_unit_theoretical'] = (data and data.qty_unit) or 0
        val['dimension_m2_theoretical'] = (data and data.qty_m2) or 0

        # is_raw:
        #   new_quantity = th_qty +/- dimension_m2_new
        #   >> th_qty = qty actual del producto,
        #   >> dimension_m2_new = qty nueva referente a una [dimensión, producto] en particular,
        data = self.pool.get('product.product').browse(cr, uid, [pro_id], context=None)[0]
        th_qty = data.qty_available

        # new_qty = th_qty - (dim_m2_theoretical - dim_m2_new)
        diff = val['dimension_m2_theoretical'] - val['dimension_m2_new']
        val['new_quantity'] = th_qty - diff

        # set uom >> m2
        val['dimension_uom_theoretical'] = uom

        #_logger.info(">> calculate_dim >> 1- val = %s", val)
        #_logger.info(">> calculate_dim >> 2- dimension_unit_new = %s", val['dimension_unit_new'])
        #_logger.info(">> calculate_dim >> 3- dimension_m2_new   = %s", val['dimension_m2_new'])
        #_logger.info(">> calculate_dim >> 4- dimension_unit_th  = %s", val['dimension_unit_theoretical'])
        #_logger.info(">> calculate_dim >> 5- dimension_m2_th    = %s", val['dimension_m2_theoretical'])
        return val

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
        #_logger.info(">> change_product_qty >> 1- ids = %s", ids)
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

            line_data = {
                'inventory_id':     inventory_id,
                'location_id':      data.location_id.id,
                'prod_lot_id':      data.lot_id.id,

                'product_id':       data.product_id.id,
                'product_qty':      data.new_quantity,  # is_raw >> es lo mismo que 'dimension_m2_new'
                'theoretical_qty':  th_qty,
                'product_uom_id':   data.product_uom.id,

                # add dimension data...
                'is_raw': data.is_raw,
                #'is_raw' : (data.prod_type == comm.RAW),
                'dimension_id': data.dimension_id.id or False,
                'dimension_unit': data.dimension_unit_new,      # new units (manual adjustment)
                'dimension_m2': data.dimension_m2_new,          # new m2 (manual adjustment)
                'dimension_unit_theoretical': data.dimension_unit_theoretical,  # old units (existing units registered [x system])
                'dimension_m2_theoretical': data.dimension_m2_theoretical,      # old m2 (existing m2 registered [x system])
            }
            #_logger.info(">> ch >> 1- line_data         = %s", line_data)
            #_logger.info(">> ch >> 2- is_raw            = %s", line_data['is_raw'])
            #_logger.info(">> ch >> 3- dimension_id      = %s", line_data['dimension_id'])
            #_logger.info(">> ch >> 4- dimension_unit    = %s", line_data['dimension_unit'])
            #_logger.info(">> ch >> 5- dimension_m2      = %s", line_data['dimension_m2'])
            #_logger.info(">> ch >> 6- dimension_unit_th = %s", line_data['dimension_unit_theoretical'])
            #_logger.info(">> ch >> 7- dimension_m2_th   = %s", line_data['dimension_m2_theoretical'])

            inventory_line_obj.create(cr, uid, line_data, context=context)
            inventory_obj.action_done(cr, uid, [inventory_id], context=context)
        return {}

stock_change_product_qty()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
