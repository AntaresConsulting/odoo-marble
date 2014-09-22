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

from openerp import models, api, _
from openerp.osv import osv
from openerp.osv import fields
# from openerp.tools.translate import _
from operator import itemgetter

import _common as comm
import logging
_logger = logging.getLogger(__name__)

# class stock_picking(osv.osv):
#    _inherit = "stock.picking"
#
#    _tipo_de_move = [
#            ('raw', 'Raw'),
#            ('insu', 'Input'),
#            ('bac', 'Bacha'),
#    ]
#
#    def _get_tipo_de_move(self, cr, uid, context=None):
#        return sorted(self._tipo_de_move, key=itemgetter(1))
#
#    _columns = {
#        'move_prod_type': fields.selection(_get_tipo_de_move, string='Product Type picking', select=True),
#    }
#
# stock_picking()

# class stock_picking_in(osv.osv):
#     _inherit = "stock.picking.in"
#
#    _tipo_de_move = [
#            ('raw', 'Raw'),
#            ('insu', 'Input'),
#            ('bac', 'Bacha'),
#    ]
#
#    def _get_tipo_de_move(self, cr, uid, context=None):
#        return sorted(self._tipo_de_move, key=itemgetter(1))
#
#    _columns = {
#        'move_prod_type': fields.selection(_get_tipo_de_move, string='Product Type picking', select=True),
#    }
#
# stock_picking_in()

class stock_move(osv.osv):
    _inherit = "stock.move"

    def _get_sign(self, obj=None):
        if not obj:
            return 0

        inp = (not obj.picking_id and obj.location_id.usage in ['customer','supplier']) or \
              (obj.picking_id and obj.picking_id.type == 'in')
        if inp:
            return 1

        out = (not obj.picking_id and obj.location_dest_id.usage in ['customer','supplier']) or \
              (obj.picking_id and obj.picking_id.type == 'out')
        if out:
            return -1

        return 0

    def _get_sign_qty(self, cr, uid, ids, field_name, arg, context=None):
        # _logger.info(">> _get_field_with_sign >> 0 >> ids = %s", ids)
        # _logger.info(">> _get_field_with_sign >> 1 >> field_name = %s", field_name)
        # _logger.info(">> _get_field_with_sign >> 2 >> arg = %s", arg)
        # _logger.info(">> _get_field_with_sign >> 3 >> context = %s", context)

        if not ids:
            return {}

        res = {}
        bal = 0.00

        ids_by_date = self.search(cr, uid, [('id','in',ids)], order='date')
        for m in self.browse(cr, uid, ids_by_date):

            fields = {}
            sign = self._get_sign(m)

            fields['qty_dimension'] = sign * m.dimension_qty
            fields['qty_product'] = sign * m.product_qty

            _logger.info(">> _get_field_with_sign >> 88 >> bal = %s", bal)
            bal += fields['qty_product']
            _logger.info(">> _get_field_with_sign >> 99 >> bal = %s", bal)

            fields['qty_balance'] = bal

            res[m.id] = fields

        _logger.info(">> _get_field_with_sign >> 5 >> res = %s", res)
        return res


    def _is_raw(self, cr, uid, ids, field_name, arg, context=None):
        """
        Determina si [ids stock_move] tiene  producto, del tipo is_raw si/no...
        """
        res = {}
        if not ids:
            return res

        # para cada stock_move -> recupero su correspondiente prod_id
        prod_ids = [sm.product_id.id for sm in self.browse(cr, uid, ids)]

        # recupero is_raw por cada producto: {prod_id: is_raw}
        data = comm.is_raw_material_by_product_id(self, cr, uid, prod_ids)

        # convierto de {prod_id: is_raw} -> {stock_move_id: is_raw}:
        res = {ids[k]: (data[prod_ids[k]] or False) for k in range(len(ids))}

        # _logger.info("10 >> _is_raw >> res = %s", res)
        return res

    def _get_move_name(self, cr, uid, pro_id=False, dim_id=False):
        name = ''
        if not pro_id:
            return name

        obj_pro = self.pool.get('product.product')
        name = obj_pro.name_get(cr, uid, [pro_id], context=None)[0][1]

        if not dim_id or \
           not comm.is_raw_material_by_product_id(self, cr, uid, [pro_id])[pro_id]:
            return name

        obj_dim = self.pool.get('product.marble.dimension')
        d = obj_dim.browse(cr, uid, [dim_id])[0]

        name = "%s >> %s" % (name, d.dimension)
        return name

    # ------------------------------------------------------------------------
    def onchange_product_id(self, cr, uid, ids, prod_id=False, loc_id=False, loc_dest_id=False, partner_id=False):

        res = super(stock_move, self).onchange_product_id(cr, uid, ids, prod_id, loc_id, loc_dest_id, partner_id)
        # _logger.info(">> onchange_product_id >> 1- res = %s", res)

        v = {}
        if (not res) or (not prod_id):
            return v

        no_prod_id = ('product_id' not in res['value'])
        if no_prod_id:
            res['value'].update({'product_id':prod_id})

        v = self.calculate_dim(cr, uid, res['value'])

        if no_prod_id:
            del v['product_id']

        res['value'].update(v)
        # _logger.info(">> onchange_product_id >> 2- res = %s", res)
        return res

    def onchange_calculate_dim(self, cr, uid, ids, pro_id, pro_uom, pro_qty, dim_id, dim_qty):
        v = {
            'product_id'      : pro_id,
            'product_uom'     : pro_uom,
            'product_uom_qty' : pro_qty,
            'dimension_id'    : dim_id,
            'dimension_qty'   : dim_qty,
            'is_raw'          : False,
        }

        # _logger.info(">> onchange_calculate_dim >> 0- val = %s", val)
        val = self.calculate_dim(cr, uid, v)

        # _logger.info(">> onchange_calculate_dim >> 1- val = %s", val)
        return {'value': val}

    def calculate_dim(self, cr, uid, val):
        # _logger.info(" >> calculate_dim >> 100- val = %s", val)

        pro_id  = val.get('product_id', False)
        pro_uom = val.get('product_uom', False)
        pro_uos = val.get('product_uos', False)
        pro_qty = val.get('product_uom_qty', 0.00)
        dim_id  = val.get('dimension_id', False)
        dim_qty = val.get('dimension_qty', 0.00)
        is_raw  = val.get('is_raw', False)

        if not pro_id:
            return val

        m2 = 0.00
        is_raw = comm.is_raw_material_by_product_id(self, cr, uid, [pro_id])[pro_id]

        if not is_raw:
            val['description'] = self._get_move_name(cr, uid, pro_id, dim_id)
            val['is_raw'] = False
            return val

        # is_raw
        if dim_id:
            obj  = self.pool.get('product.marble.dimension')
            data = obj.read(cr, uid, [dim_id], ['m2'], context=None)
            m2   = data[0]['m2'] if (len(data) > 0 and len(data[0]) > 0) else 0.00

        pro_qty = dim_qty * m2
        pro_uom = comm.get_uom_m2_id(self,cr,uid)

        v = {}
        v['product_id']      = pro_id
        v['product_uos']     = pro_uos
        v['product_uom']     = pro_uom
        v['product_uom_qty'] = pro_qty
        v['dimension_id']    = dim_id
        v['dimension_qty']   = dim_qty
        v['is_raw']          = is_raw
        v['description']     = self._get_move_name(cr, uid, pro_id, dim_id)

        # _logger.info(" >> calculate_dim >> 101- v = %s", v)
        return v

    # ------------------------------------------------------------------------
    def _check_data_before_save(self, cr, uid, sm_id, val):
        _logger.info(">> _check_data_before_save >> 1- val = %s", val)

        # defino campos a evaluar
        fields_list = ['product_id','product_uom','product_uom_qty','dimension_id','dimension_qty','is_raw', 'description']

        # si (NO existe algun elemento de [fields_list] en [val]) >> me voy, no precesar...
        if not any(e in fields_list for e in val.keys()):
            return

        to_update = {}
        no_update = {}
        obj = (sm_id and self.pool.get('stock.move').browse(cr, uid, sm_id)) or None

        # divido [info suministrada por actuatizar] e [info calculada, no para actualizar, requerida]
        for field in fields_list:

            if (field in val):
                to_update[field] = val[field]
                continue

            # >> si (field es 'read-only') >> la data no viaja...
            elif (field in ['product_uom', 'product_uom_qty', 'description']):
                to_update[field] = val.get(field,'')
                continue

            else:
                no_update[field] = (obj and (obj[0][field].id if ('class' in str(type(obj[0][field]))) else obj[0][field])) or False

        param = dict(to_update.items() + no_update.items())
        v = self.calculate_dim(cr, uid, param)

        # actualizo valores de retorno
        for field in to_update:
            val[field] = v[field]

        # _logger.info(">> _check_data_before_save >> 23 >> val = %s", val)
        return

    def create(self, cr, uid, data, context=None):
        self._check_data_before_save(cr, uid, [], data)
        return super(stock_move, self).create(cr, uid, data, context=context)


    def write(self, cr, uid, ids, vals, context=None):
        for ms_id in ids:
            self._check_data_before_save(cr, uid, ms_id, vals)
        return super(stock_move, self).write(cr, uid, ids, vals, context=context)

    # --- overwriter: registro en balance ---
    def action_done(self, cr, uid, ids, context=None):
        _logger.info(">> _action_done >> 00 >> ok - ids = %s", ids)

        if not super(stock_move, self).action_done(cr, uid, ids, context=context):
            return False

        obj_bal = self.pool.get('product.marble.dimension.balance')
        obj_mov = [move for move in self.browse(cr, uid, ids, context=context) if move.state == 'done' and move.product_id.is_raw]

        _logger.info(">> _action_done >> 01 >> obj_mov = %s", obj_mov)
        if not obj_mov:
            return True

        # obj_mov is raw -> verifico:
        # >> si (move.location = stock_loc or move.location_dest = stock_loc)
        #    >> registro en Balance.
        stock_loc = comm.get_location_stock(self, cr, uid)
        bal_list = [mov for mov in obj_mov if stock_loc in [mov.location_id.id, mov.location_dest_id.id]]

        _logger.info(">> _action_done >> 02 >> stock_loc = %s", stock_loc)
        _logger.info(">> _action_done >> 03 >> bal_list = %s", bal_list)
        for mov in bal_list:
            val = {
                'prod_id': mov.product_id.id,
                'dim_id': mov.dimension_id.id,
                'dimension_qty': mov.dimension_qty,
                'dimension_m2': mov.product_uom_qty,
                'typeMove': 'in' if stock_loc == mov.location_dest_id.id else 'out'
            }

            _logger.info(">> _action_done >> 04- val = %s", val)
            obj_bal.register_balance(cr, uid, val, context)

        return True

    _columns = {
        'description': fields.char('Description'),
        'dimension_id': fields.many2one('product.marble.dimension', 'Dimension', select=True, states={'done': [('readonly', True)]}, domain=[('state','=','done')]),
        'dimension_qty': fields.integer('Units', size=3, states={'done': [('readonly', True)]}),
        'is_raw': fields.function(_is_raw, type='boolean', string='Is Marble'),

        'partner_picking_id': fields.related('picking_id', 'partner_id', type='many2one', relation='res.partner', string='Patern', store=False),

        'qty_dimension': fields.function(_get_sign_qty, string='Dimension Qty', multi="sign"),
        'qty_product': fields.function(_get_sign_qty, string='Product Qty', multi="sign"),
        'qty_balance': fields.function(_get_sign_qty, string='Balance Qty', multi="sign"),
    }


    _defaults = {
        'dimension_id': False,
        'dimension_qty': 0,
    }

stock_move()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
