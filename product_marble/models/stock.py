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
from openerp.osv import osv, fields
# from openerp.tools.translate import _
from operator import itemgetter

import inspect

import _common as comm
import logging
_logger = logging.getLogger(__name__)

class stock_picking(osv.osv):
    _name = "stock.picking"
    _inherit = "stock.picking"
    _description = "Picking List"

    _tipo_de_move = [
            ('raw', 'Raw'),
            ('insu', 'Input'),
            ('bac', 'Bacha'),
    ]

    def _get_tipo_de_move(self, cr, uid, context=None):
        return sorted(self._tipo_de_move, key=itemgetter(1))

    def _get_types(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for pick in self.browse(cr, uid, ids):
            if len(pick.move_lines) > 0:
                res.update({pick.id : pick.move_lines[0].prod_type})
        return res

    @api.cr_uid_ids_context
    def do_enter_transfer_details_marble(self, cr, uid, picking, context=None):
	resp = super(stock_picking, self).do_enter_transfer_details(cr, uid, picking, context=context)	
	return resp['res_id']	


    _columns = {
        'move_prod_type': fields.selection(_get_tipo_de_move, string='Product Type picking', select=True),
        'prod_type': fields.function(_get_types, type='char', string='Product Type', store=False),
        #'prod_type' : fields.related('product_id', 'prod_type', type='char', relation='product.template', string='Product Type'),
    }

#    @api.cr_uid_ids_context
#    def do_prepare_partial(self, cr, uid, picking_ids, context=None):
#        super(stock_picking, self).do_prepare_partial(cr, uid, picking_ids, context=context)
#        _logger.info('>> do_prepare_partial >> 1- picking_ids = %s', picking_ids)

#    def _prepare_values_extra_move(self, cr, uid, op, product, remaining_qty, context=None):
#        res = super(stock_picking, self)._prepare_values_extra_move(cr, uid, op, product, remaining_qty, context)
#        _logger.info('>> _prepare_values_extra_move >> 1- res = %s', res)
#        res.update({
#            'dimension_id': op.dimension_id.id,
#            'dimension_unit': op.dimension_unit,
#           })
#        _logger.info('>> _prepare_values_extra_move >> 2- res = %s', res)
#        return res

stock_picking()

class stock_pack_operation(osv.osv):
    _name = "stock.pack.operation"
    _inherit = "stock.pack.operation"
    _description = "Packing Operation"

    #dimension_id = openerp.fields.Many2one('product.marble.dimension', string='Dimension', ondelete='set null')
    #dimension_unit = openerp.fields.Integer(string='Units')
    #prod_type = openerp.fields.Char(related='product_id.prod_type', string='Product Type')
    _columns = {
        'dimension_id': fields.many2one('product.marble.dimension', 'Dimension', domain=[('state','=','done')]),
        'dimension_unit': fields.integer('Units', size=3),   # units
        'prod_type' : fields.related('product_id', 'prod_type', type='char', relation='product.template', string='Product Type'),
    }

    _defaults = {
        'dimension_id': False,
        'dimension_unit': 0,
    }

    def _before_save(self, cr, uid, vals, context):
        obj_pick = self.pool.get('stock.picking')
        pick_id = vals.get('picking_id',False)
        prod_id = vals.get('product_id',False)

        # localizo el 'stock_move' x picking + product, luego obteng su units a registrar en stock.pack.operation.-
        for mov in obj_pick.browse(cr, uid, pick_id, context=context).move_lines:
            if mov.product_id.id == prod_id and mov.product_id.prod_type == comm.RAW:
                vals.update(dimension_id = mov.dimension_id.id)
                vals.update(dimension_unit = mov.dimension_unit)
                break

    def create(self, cr, uid, vals, context=None):
        self._before_save(cr, uid, vals, context)
        #_logger.info('>> stock_pack_opetarion >> create >> 12- vals = %s', vals)
        return super(stock_pack_operation, self).create(cr, uid, vals, context=context)

    def write(self, cr, uid, ids, vals, context=None):
        _logger.info('>> stock_pack_opetarion >> write >> 20- vals = %s', vals)
        self._before_save(cr, uid, vals, context)

        _logger.info('>> stock_pack_opetarion >> write >> 21- vals = %s', vals)
        return super(stock_pack_operation, self).write(cr, uid, ids, vals, context=context)

stock_pack_operation()

class stock_move(osv.osv):
    _inherit = "stock.move"

    # defino tipo de movimiento en Locacion de Stock:
    # return 0 = no afecta a Stock,
    #        1 = entra prod. en Stock (in: input),
    #       -1 = sale prod. en Stock (out: output)
    def stock_move(self, cr, uid, mov=None):
        if not mov:
            return 0   # none
        stock_loc = comm.get_location_stock(self, cr, uid)
        if stock_loc == mov.location_dest_id.id:
            return 1   # input to Stock
        if stock_loc == mov.location_id.id:
            return -1  # output to Stock
        return 0  # none

    def _get_sign_qty(self, cr, uid, ids, field_name, arg, context=None):
        if not ids:
            return {}

        res = {}
        bal = 0.00
        ids_by_date = self.search(cr, uid, [('id','in',ids)], order='date')
        for m in self.browse(cr, uid, ids_by_date):
            fields = {}
            # sign = self._get_sign(m)
            sign = self.stock_move(cr, uid, m)

            fields['qty_dimension'] = sign * m.dimension_unit
            fields['qty_product'] = sign * m.product_qty

            bal += fields['qty_product']
            fields['qty_balance'] = bal

            res[m.id] = fields
        # _logger.info(">> _get_field_with_sign >> 5 >> res = %s", res)
        return res

    def _get_types(self, cr, uid, ids, field_name, arg, context=None):
        #_logger.info(">> _get_types >> 1- ids = %s", ids)
        res = {}
        if not ids: return res
        if not isinstance(ids, (list,tuple)): ids = [ids]

        types = comm.get_prod_types(self, cr, uid, context)
        #_logger.info(">> _get_types >> 2- types = %s", types)

        for ms_id in self.browse(cr, uid, ids, context):
            cid = ms_id.product_id.categ_id.id
            #_logger.info(">> _get_types >> 3- cid = %s", cid)
            res.update({ms_id.id : types.get(cid,'*')})

        #_logger.info(">> _get_types >> 4- res = %s", res)
        return res


    def _is_raw(self, cr, uid, ids, field_name, arg, context=None):
        #"""
        #Determina si [ids stock_move] tiene  producto, del tipo is_raw si/no...
        #"""
        #res = {}
        #if not ids:
        #    return res

        # para cada stock_move -> recupero su correspondiente prod_id
        #prod_ids = [sm.product_id.id for sm in self.browse(cr, uid, ids)]

        # recupero is_raw por cada producto: {prod_id: is_raw}
        #data = comm.is_raw_material_by_product_id(self, cr, uid, prod_ids)

        # convierto de {prod_id: is_raw} -> {stock_move_id: is_raw}:
        #res = {ids[k]: (data[prod_ids[k]] or False) for k in range(len(ids))}

        # _logger.info("10 >> _is_raw >> res = %s", res)
        #return res
        res = { sm.id : (sm.product_id.prod_type == comm.RAW) for sm in self.browse(cr, uid, ids) }
        #_logger.info("10 >> _is_raw >> res = %s", res)
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
        #_logger.info(">> onchange_product_id >> 1- res = %s", res)

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
        #_logger.info(">> onchange_product_id >> 2- res = %s", res)
        return res

    def onchange_calculate_dim(self, cr, uid, ids, pro_id, pro_uom, pro_qty, dim_id, dim_unit):
        v = {
            'product_id'      : pro_id,
            'product_uom'     : pro_uom,
            'product_uom_qty' : pro_qty,
            'dimension_id'    : dim_id,
            'dimension_unit'   : dim_unit,
            'is_raw'          : False,
            'prod_type'       : comm.OTHER,
        }

        # _logger.info(">> onchange_calculate_dim >> 0- val = %s", val)
        val = self.calculate_dim(cr, uid, v)

        # _logger.info(">> onchange_calculate_dim >> 1- val = %s", val)
        return {'value': val}

    def calculate_dim(self, cr, uid, val):
        #_logger.info(" >> calculate_dim >> 100- val = %s", val)

        pro_id  = val.get('product_id', False)
        pro_uom = val.get('product_uom', False)
        pro_uos = val.get('product_uos', False)
        pro_qty = val.get('product_uom_qty', 0.00)
        dim_id  = val.get('dimension_id', False)
        dim_unit = val.get('dimension_unit', 0.00)
        is_raw  = val.get('is_raw', False)
        prod_type = val.get('prod_type', comm.OTHER)

        if not pro_id:
            return val

        #pro = self.pool.get('product.product').browse(cr, uid, pro_id)
        #_logger.info(" >> calculate_dim >> 1- prod = %s", pro)

        #pro = self.pool.get('product.product').browse(cr, uid, pro_id).categ_id
        #_logger.info(" >> calculate_dim >> 2- prod = %s", pro)

        #cid = self.pool.get('product.product').browse(cr, uid, pro_id).categ_id.id
        #prod_type = comm.get_prod_types(self, cr, uid).get(cid, comm.OTHER)
        #val['prod_type'] = prod_type
        prod_type = self.pool.get('product.product').browse(cr, uid, pro_id).prod_type
        val['prod_type'] = prod_type

        m2 = 0.00
        #is_raw = comm.is_raw_material_by_product_id(self, cr, uid, [pro_id])[pro_id]
        is_raw = (prod_type == comm.RAW)

        if prod_type not in ('raw', 'bacha'):
            val['description'] = self._get_move_name(cr, uid, pro_id, dim_id)
            return val

        elif prod_type == 'bacha':
            val['description'] = self._get_move_name(cr, uid, pro_id, dim_id)
            val['product_uom'] = comm.get_uom_units_id(self,cr,uid)
            return val

        m2 = 0.00
        if dim_id:
            #obj  = self.pool.get('product.marble.dimension')
            #data = obj.read(cr, uid, [dim_id], ['m2'], context=None)
            #m2   = data[0]['m2'] if (len(data) > 0 and len(data[0]) > 0) else 0.00
            m2 = self.pool.get('product.marble.dimension').browse(cr, uid, dim_id).m2

        pro_qty = dim_unit * m2
        pro_uom = comm.get_uom_m2_id(self,cr,uid)

        v = {}
        v['product_id']      = pro_id
        v['product_uos']     = pro_uos
        v['product_uom']     = pro_uom
        v['product_uom_qty'] = pro_qty
        v['dimension_id']    = dim_id
        v['dimension_unit']  = dim_unit
        v['is_raw']          = is_raw
        v['prod_type']       = prod_type
        v['description']     = self._get_move_name(cr, uid, pro_id, dim_id)

        #_logger.info(" >> calculate_dim >> 101- v = %s", v)
        return v

    # ------------------------------------------------------------------------
    def _check_data_before_save(self, cr, uid, sm_id, val):
        #_logger.info(">> _check_data_before_save >> 1- sm_id = %s", sm_id)
        #_logger.info(">> _check_data_before_save >> 2- val = %s", val)
        if  'product_id' not in val: return

        # defino campos a evaluar
        fields_list = ['product_id','product_uom','product_uom_qty','dimension_id','dimension_unit','is_raw','description']

        # si (NO existe algun elemento de [fields_list] en [val]) >> me voy, no precesar...
        if not any(e in fields_list for e in val.keys()):
            return

        to_update = {}
        no_update = {}
        obj = (sm_id and self.pool.get('stock.move').browse(cr, uid, sm_id)) or False
        #_logger.info(">> _check_data_before_save >> 3- obj = %s", obj)

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
            if (field not in val) and (not v[field]):
               # no copiarlo...
               pass
            else:
                val[field] = v[field]

        # -------------------------------------------------
        # si 'is_raw' >> valido datos requeridos...
        valu = v
        mov = obj and obj[0]
        #_logger.info(">> _check_data_before_save >> 6- mov = %s", mov)

        is_raw  = valu.get('is_raw',False) or (mov and mov.is_raw)
        dim_id  = valu.get('dimension_id',0) or (mov and mov.dimension_id.id)
        dim_unit = valu.get('dimension_unit',0) or (mov and mov.dimension_unit)
        pro_qty = valu.get('product_uom_qty',0) or (mov and mov.product_uom_qty)

        msg = self._check_data_required(cr, uid, is_raw, dim_id, dim_unit, pro_qty)
        if msg:
            raise osv.except_osv(_('Error'), _(msg))
        return

    def _check_data_required(self, cr, uid, is_raw, dim_id, dim_unit, prod_qty):
        if not is_raw:
            return ''
        if not dim_id:
            return 'You cannot save a Move-Stock without Dimension (id)'
        if not dim_unit:
            return 'You cannot save a Move-Stock without Quantity Dimension (qty)'
        if not prod_qty:
            return 'You cannot save a Move-Stock without Quantity Product (uom qty)'
        return ''
    # ------------------------------------------------------------------------

    def create(self, cr, uid, data, context=None):
        #_logger.info('>> stock_move >> create >> 1- data = %s', data)
        self._check_data_before_save(cr, uid, [], data)

        #_logger.info('>> stock_move >> create >> 2- data = %s', data)
        return super(stock_move, self).create(cr, uid, data, context=context)

    def write(self, cr, uid, ids, vals, context=None):
        #for ms_id in ids:
        #    self._check_data_before_save(cr, uid, ms_id, vals)
        #_logger.info('>> stock_move >> write >> 11- ids = %s', ids)
        #_logger.info('>> stock_move >> write >> 12- vals = %s', vals)

        #if len(ids) > 1:
        #    raise osv.except_osv(_('Error'), 'TODO: A corregir. Mas de un registro a escribir....')

        sm_id = ids[0] if len(ids) >= 1 else False
        self._check_data_before_save(cr, uid, sm_id, vals)

        #_logger.info('>> stock_move >> write >> 13- vals = %s', vals)
        return super(stock_move, self).write(cr, uid, ids, vals, context=context)

    # --- extend: registro en balance ---
    def action_done(self, cr, uid, ids, context=None):
        if not super(stock_move, self).action_done(cr, uid, ids, context=context):
            return False

        obj_bal = self.pool.get('product.marble.dimension.balance')
        #obj_mov = [move for move in self.browse(cr, uid, ids, context=context) if move.state == 'done' and move.product_id.is_raw]
        obj_mov = [move for move in self.browse(cr, uid, ids, context=context) if move.state == 'done' and (move.product_id.prod_type == comm.RAW)]
        if not obj_mov:
            return True

        # obj_mov is raw -> verifico:
        # >> si (move.location = stock_loc or move.location_dest = stock_loc)
        #    >> registro en Balance.
        # stock_loc = comm.get_location_stock(self, cr, uid)
        # bal_list = [mov for mov in obj_mov if stock_loc in [mov.location_id.id, mov.location_dest_id.id]]
        bal_list = [mov for mov in obj_mov if self.stock_move(cr, uid, mov) != 0]

        #_logger.info(">> _action_done >> 02 >> stock_loc = %s", stock_loc)
        _logger.info(">> _action_done >> 03 >> bal_list = %s", bal_list)
        for mov in bal_list:

            # valid data required
            #msg = self._check_data_required(cr, uid, mov.product_id.is_raw, mov.dimension_id, mov.dimension_unit, mov.product_uom_qty)
            is_raw = (mov.product_id.prod_type == comm.RAW)
            msg = self._check_data_required(cr, uid, is_raw, mov.dimension_id, mov.dimension_unit, mov.product_uom_qty)
            if msg:
                raise osv.except_osv(_('Error'), _(msg))

            # set data..
            val = {
                'prod_id': mov.product_id.id,
                'dim_id': mov.dimension_id.id,
                'dimension_unit': mov.dimension_unit,
                'dimension_m2': mov.product_uom_qty,
                # 'typeMove': 'in' if stock_loc == mov.location_dest_id.id else 'out'
                'typeMove': 'in' if self.stock_move(cr, uid, mov) > 0 else 'out'
            }
#            _logger.info(">> _action_done >> 04- val = %s", val)
            obj_bal.register_balance(cr, uid, val, context)

#        _logger.info(">> _action_done >> 05- OK >> val = %s", val)
        return True

    _columns = {
        'description': fields.char('Description'),
        'dimension_id': fields.many2one('product.marble.dimension', 'Dimension', select=True, states={'done': [('readonly', True)]}, domain=[('state','=','done')]),
        'dimension_unit': fields.integer('Units', size=3, states={'done': [('readonly', True)]}),

        'is_raw': fields.function(_is_raw, type='boolean', string='Is Marble'),
        #'prod_type': fields.function(_get_types, type='char', string='Product Type', store=False),
        'prod_type' : fields.related('product_id', 'prod_type', type='char', relation='product.template', string='Product Type'),

        'employee_id': fields.many2one('hr.employee', 'Empleado', select=True, states={'done': [('readonly', True)]}, domain=[('active','=',True)]),
        'employee_image': fields.related('employee_id', 'image_small', type='binary', relation='hr.employee', string='Part Number', store=True, readonly=True),

        #'employee': fields.many2one('hr.employee', 'Empleado', select=True, states={'done': [('readonly', True)]}, domain=[('active','=',True)]),

        'partner_picking_id': fields.related('picking_id', 'partner_id', type='many2one', relation='res.partner', string='Patern', store=False),

        'qty_dimension': fields.function(_get_sign_qty, string='Unidades', multi="sign"),
        'qty_product': fields.function(_get_sign_qty, string='Area (m2)', multi="sign"),
        'qty_balance': fields.function(_get_sign_qty, string='Balance (m2)', multi="sign"),
    }

    _defaults = {
        'dimension_id': False,
        'dimension_unit': 0,
    }

stock_move()


class stock_inventory_line(osv.osv):
    _inherit = "stock.inventory.line"
    _name = "stock.inventory.line"
    _description = "Inventory Line"

    _columns = {
        'is_raw': fields.boolean('Is Raw', readonly=True),
        'dimension_id': fields.many2one('product.marble.dimension', 'Dimension', domain=[('state','=','done')]),
        'dimension_unit': fields.integer('Real Dim. [Units]', size=3),   # units
        'dimension_m2': fields.float('Real Dim. [M2]', digits=(5,3)),  # m2
        'dimension_unit_theoretical': fields.integer('Theoretical Dim. [Units]', size=3, readonly=True),  # units
        'dimension_m2_theoretical': fields.float('Theoretical Dim. [M2]', digits=(5,3), readonly=True),  # m2
    }

    defaults = {
        'is_raw': False,
        'dimension_id': False,
        'dimension_unit': 0,
        'dimension_m2': 0,
        'dimension_unit_theoretical': 0,
        'dimension_m2_theoretical': 0,
    }

    # overwrite: stock > stock_inventory_line - odoo v8.0 - line: 2727 - 27555
    # sobre escribo metodo para incorporar 'dimensiones' en caso de ser materia prima
    def _resolve_inventory_line(self, cr, uid, inventory_line, context=None):
        stock_move_obj = self.pool.get('stock.move')

        if inventory_line.is_raw:
            diff_unit = inventory_line.dimension_unit_theoretical - inventory_line.dimension_unit
            diff = inventory_line.dimension_m2_theoretical - inventory_line.dimension_m2
        else:
            diff = inventory_line.theoretical_qty - inventory_line.product_qty

        if not diff:
            return

        # each theorical_lines where difference between theoretical and checked quantities is not 0 is a line for which we need to create a stock move
        vals = {
            'name': _('INV:') + (inventory_line.inventory_id.name or ''),
            'product_id': inventory_line.product_id.id,
            'product_uom': inventory_line.product_uom_id.id,
            'date': inventory_line.inventory_id.date,
            'company_id': inventory_line.inventory_id.company_id.id,
            'inventory_id': inventory_line.inventory_id.id,
            'state': 'confirmed',
            'restrict_lot_id': inventory_line.prod_lot_id.id,
            'restrict_partner_id': inventory_line.partner_id.id,
            'dimension_id': inventory_line.dimension_id.id      # dimension
        }

        inventory_location_id = inventory_line.product_id.property_stock_inventory.id
        if diff < 0:
            # found more than expected
            vals['location_id'] = inventory_location_id
            vals['location_dest_id'] = inventory_line.location_id.id
            vals['product_uom_qty'] = -diff                                      # dim >> m2 [faltante]
            vals['dimension_unit'] = (inventory_line.is_raw and -diff_unit) or 0  # dim >> unidades [faltante]
        else:
            # found less than expected
            vals['location_id'] = inventory_line.location_id.id
            vals['location_dest_id'] = inventory_location_id
            vals['product_uom_qty'] = diff                                      # dim >> m2 [excedente]
            vals['dimension_unit'] = (inventory_line.is_raw and diff_unit) or 0  # dim >> unidades [excedente]

        _logger.info(">> _resolve_inventory_line >> 01- vals = %s", vals)
        return stock_move_obj.create(cr, uid, vals, context=context)

stock_inventory_line()




#
