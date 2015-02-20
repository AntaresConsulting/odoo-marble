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

from openerp import api, models, fields as _fields
from openerp.osv import osv
from openerp.osv import fields
from openerp.tools.translate import _
from operator import itemgetter
import _common as comm
# import pdb
#import psycopg2

import logging
_logger = logging.getLogger(__name__)

class product_category(models.Model):
    _inherit = "product.category"
    _name = "product.category"

    prod_type = _fields.Char(string='Product Type')

    def name_get(self, cr, uid, ids, context=None):
        # _logger.info(">> name_get >> 0- ids = %s", ids)
        if isinstance(ids, (list, tuple)) and not len(ids):
            return []
        if isinstance(ids, (long, int)):
            ids = [ids]
        res = []
        ids_by_name = self.search(cr, uid, [('id','in',ids)], order='name')
        for cat in self.browse(cr, uid, ids_by_name, context=context):
            res.append((cat.id, cat.name))
        # _logger.info(">> name_get >> 3- res = %s", res)
        return res

#    def name_get(self):
#        return self.search_read([],['name'])


product_category()


class product_template(osv.osv):
    _name = 'product.template'
    _inherit = 'product.template'

    _material = [
            ('mar', 'Marmol'),
            ('gra', 'Granito'),
            ('qua', 'Quarzo'),
    ]

    _color = [
            ('bla', 'Blanco'),
            ('neg', 'Negro'),
            ('ros', 'Rosa'),
            ('ver', 'Verde'),
            ('azu', 'Azul'),
            ('cel', 'Celeste'),
            ('lil', 'Lila'),
            ('ama', 'Amarillo'),
            ('roj', 'Rojo'),
            ('gri', 'Gris'),
            ('mar', 'Marron'),
            ('bei', 'Beige'),
    ]

    _finished = [
            ('lus', 'Lustrado'),
            ('apo', 'Aponazado'),
            ('fla', 'Flameado'),
            ('rus', 'Rustico'),
            ('lea', 'Leather'),
    ]

    _bacha_material = [
            ('los', 'Losa'),
            ('ace', 'Acero'),
    ]

    _bacha_marca = [
            ('joh', 'Johnson Acero'),
            ('mip', 'Mi Pileta'),
            ('roc', 'Roca'),
            ('fer', 'Ferrum'),
            ('cer', 'Cerart'),
            ('fra', 'Franke'),
            ('ari', 'Ariel Del Plata'),
            ('dec', 'Deca Piazza'),
    ]

    _bacha_acero = [
            ('403', 'Acero 403'),
            ('304', 'Acero 304'),
    ]

    _bacha_tipo = [
            ('sim', 'Simple'),
            ('dob', 'Doble'),
            ('red', 'Redonda'),
    ]

    _bacha_colocacion = [
            ('enc', 'Encastre'),
            ('peg', 'Pegar de Abajo'),
    ]

    @api.model
    def _get_material(self):
        return sorted(self._material, key=itemgetter(1))

    @api.model
    def _get_color(self):
        return sorted(self._color, key=itemgetter(1))

    @api.model
    def _get_finished(self):
        return sorted(self._finished, key=itemgetter(1))

    @api.model
    def _get_bacha_tipo(self):
        return sorted(self._bacha_tipo, key=itemgetter(1))

    @api.model
    def _get_bacha_colocacion(self):
        return sorted(self._bacha_colocacion, key=itemgetter(1))

    @api.model
    def _get_bacha_acero(self):
        return sorted(self._bacha_acero, key=itemgetter(1))

    @api.model
    def _get_bacha_material(self):
        return sorted(self._bacha_material, key=itemgetter(1))

    @api.model
    def _get_bacha_marca(self):
        return sorted(self._bacha_marca, key=itemgetter(1))

    def _get_categ_name(self, cr, uid, ids, field_name, arg, context=None):
        # _logger.info("09 >> _get_categ_str >> ids = %s", ids)
        res = {}
        if not ids:
            return res
        for p in self.browse(cr, uid, ids, context=context):
            if comm.is_raw_material(self, cr, uid, p.categ_id):
                res[p.id] = 'raw'
            elif comm.is_bachas(self, cr, uid, p.categ_id):
                res[p.id] = 'bac'
            elif comm.is_inputs(self, cr, uid, p.categ_id):
                res[p.id] = 'inp'
            elif comm.is_services(self, cr, uid, p.categ_id):
                res[p.id] = 'ser'
            else:
                res[p.id] = '*'
        # _logger.info("10 >> _get_categ_str >> res = %s", res)
        return res


    def _get_uom_readonly(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        if not ids:
            return res
        for p in self.browse(cr, uid, ids, context=context):
            ro = comm.is_raw_material(self, cr, uid, p.categ_id.id) or \
                 comm.is_bachas(self, cr, uid, p.categ_id.id)
            res[p.id] = ro
        # _logger.info("11 >> _get_readonly >> res = %s", res)
        return res

#    def _is_raw_material(self, cr, uid, ids, field_name, arg, context=None):
#       return comm.is_raw_material_by_product_id(self, cr, uid, ids)

#    @api.multi
#    def _is_raw_material(self, value):
#        return { rec.id:(rec.prod_type == comm.RAW) for rec in self }

#    @api.multi
#    def _is_bacha(self, value):
#       return { rec.id:(rec.prod_type == comm.BACHA) for rec in self }

#    @api.multi
#    def _is_input(self, value):
#       return { rec.id:(rec.prod_type == comm.INPUT) for rec in self }

    def _get_categ_raw_material_id(self, cr, uid, ids, field_name, arg, context=None):
        cid = comm.get_raw_material_id(self, cr, uid)
        res = {}.fromkeys(ids,[cid])
        # _logger.info(">> _get_categ_raw_material_id >> 88 >> res = %s", res)
        return res

    def _get_categ_marble_domain(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        if not ids:
            return res
        cid = comm.get_raw_material_id(self, cr, uid)
        res = {}.fromkeys(ids,[cid])
        # _logger.info(">> _get_categ_marble_domain >> 2 >> res = %s", res)
        return res

    @api.onchange('categ_id')
    def _onchange_category_id(self):
        if not self.categ_id:
            return
        #cid = self.categ_id.id
        self.prod_type         = self.categ_id.prod_type
        #self.is_raw           = False
        #self.is_bacha         = False
        #self.is_input         = False
        #self.uom_readonly     = False

        self.raw_material     = False
        self.raw_color        = False
        self.raw_finished     = False

        self.bacha_material   = False
        self.bacha_marca      = False
        self.bacha_acero      = False
        self.bacha_colocacion = False
        self.bacha_tipo       = False
        self.bacha_ancho      = False
        self.bacha_largo      = False
        self.bacha_prof       = False
        self.bacha_diam       = False

        #if comm.is_raw_material(self, cid):
        #    self.type         = 'product'
        #    self.is_raw       = True
        #    self.uom_readonly = True
        #    self.uom_id       = comm.get_uom_m2_id(self)
        #elif comm.is_bachas(self, cid):
        #    self.type         = 'product'
        #    self.is_bacha     = True
        #    self.uom_readonly = True
        #    self.uom_id       = comm.get_uom_units_id(self)
        #elif comm.is_inputs(self, cid):
        #    self.type         = 'consu'
        #    self.is_input     = True
        #    self.uom_readonly = True
        #    self.uom_id       = comm.get_uom_units_id(self)
        #elif comm.is_services(self, cid):
        #    self.type         = 'service'

        if self.prod_type == comm.RAW:
            self.type         = 'product'
        #    self.is_raw       = True
        #    self.uom_readonly = True
            self.uom_id       = comm.get_uom_m2_id(self)
        elif self.prod_type == comm.BACHA:
            self.type         = 'product'
        #    self.is_bacha     = True
        #    self.uom_readonly = True
            self.uom_id       = comm.get_uom_units_id(self)
        elif self.prod_type == comm.INPUT:
            self.type         = 'consu'
        #    self.is_input     = True
        #    self.uom_readonly = True
            self.uom_id       = comm.get_uom_units_id(self)
        elif self.prod_type == comm.SERVICE:
            self.type         = 'service'

    @api.model
    def _validate_data_movile(self, data):
        #_logger.info(">> _validate_data_movile >> 1 >> data = %s", data)
        # --- determino categ_id ---
        categ_list = [comm.RAW, comm.BACHA, comm.SERVICE, comm.INPUT]
        field_inp  = 'movile_categ_name'
        field_out  = 'categ_id'
        if data.get(field_inp, False) in categ_list:
            field_val = data.pop(field_inp)
            cid = comm.get_prop(self, field_val)
            data.update({field_out:cid})
        #_logger.info(">> _validate_data_movile >> 2 >> data = %s", data)
        return

    @api.model
    def _check_data_before_save(self, data):
        #_logger.info(">> check_before >> 1 >> data = %s", data)

        # valido datos proveniente de 'disp. movi'
        self._validate_data_movile(data)

        if ('categ_id' not in data):
            return

        res = {}
        cid = data['categ_id']

        if comm.is_raw_material(self, cid):
            res['type']   = data.get('type', 'product')
            res['uom_id'] = data.get('uom_id', comm.get_uom_m2_id(self))
            res['uom_po_id'] = data.get('uom_po_id', comm.get_uom_m2_id(self))

        elif comm.is_bachas(self, cid):
            res['type']   = data.get('type', 'product')
            res['uom_id'] = data.get('uom_id', comm.get_uom_units_id(self))
            res['uom_po_id'] = data.get('uom_po_id', comm.get_uom_units_id(self))

        elif comm.is_inputs(self, cid):
            res['type']   = data.get('type', 'consu')

        elif comm.is_services(self, cid):
            res['type']   = data.get('type', 'service')

        is_raw   = comm.is_raw_material(self, cid)
        is_bacha = comm.is_bachas(self, cid)

        res['raw_material']     = (is_raw or is_bacha) and is_raw and data.get('raw_material',False)
        res['raw_color']        = (is_raw or is_bacha) and is_raw and data.get('raw_color',False)
        res['raw_finished']     = (is_raw or is_bacha) and is_raw and data.get('raw_finished',False)

        res['bacha_material']   = (is_raw or is_bacha) and is_bacha and data.get('bacha_material',False)
        res['bacha_marca']      = (is_raw or is_bacha) and is_bacha and data.get('bacha_marca',False)
        res['bacha_acero']      = (is_raw or is_bacha) and is_bacha and data.get('bacha_acero',False)
        res['bacha_colocacion'] = (is_raw or is_bacha) and is_bacha and data.get('bacha_colocacion',False)
        res['bacha_tipo']       = (is_raw or is_bacha) and is_bacha and data.get('bacha_tipo',False)
        res['bacha_ancho']      = (is_raw or is_bacha) and is_bacha and data.get('bacha_ancho',False)
        res['bacha_largo']      = (is_raw or is_bacha) and is_bacha and data.get('bacha_largo',False)
        res['bacha_prof']       = (is_raw or is_bacha) and is_bacha and data.get('bacha_prof',False)
        res['bacha_diam']       = (is_raw or is_bacha) and is_bacha and data.get('bacha_diam',False)

        data.update(res)

        #_logger.info(">> check_before >> 2 >> data = %s", data)
        return

    @api.model
    def create(self, val):
        self._check_data_before_save(val)
        #return super(product_product, self).create(val)
        return super(product_template, self).create(val)

    def write(self, cr, uid, ids, vals, context=None):
        self._check_data_before_save(cr, uid, vals)
        #return super(product_product, self).write(cr, uid, ids, vals, context=context)
        return super(product_template, self).write(cr, uid, ids, vals, context=context)

    def _get_attrs(self, cr, uid, ids, context=None):
        res = {}
        if not ids:
            return res
        for p in self.browse(cr, uid, ids, context=context):
            attrs = ""
            if comm.is_raw_material(self, cr, uid, p.categ_id.id):
                mat = dict(self._material).get(p.raw_material)
                col = dict(self._color).get(p.raw_color)
                fin = dict(self._finished).get(p.raw_finished)
                attrs = "%s - %s - %s" % (mat, col, fin)

            elif comm.is_bachas(self, cr, uid, p.categ_id.id):
                mat = dict(self._bacha_material).get(p.bacha_material)
                mar = dict(self._bacha_marca).get(p.bacha_marca)
                attrs = "%s - %s" % (mar, mat)

            res.update({p.id: attrs})
        # _logger.info(">> _get_attrs >> 1 >> res = %s", res)
        return res

    def _attrs_material(self, cr, uid, ids, field_name, arg, context=None):
        return self._get_attrs(cr, uid, ids, context=context)

    def name_get(self, cr, uid, ids, context=None):
        #names = super(product_product, self).name_get(cr, uid, ids, context=context)
        names = super(product_template, self).name_get(cr, uid, ids, context=context)
        if not names:
            return []
        res = []
        attrs = self._get_attrs(cr, uid, ids, context=context)
        for t in names:
            key = t[0]
            data = t[1]
            if attrs.get(key) and len(attrs.get(key)) > 0:
                data = "%s (%s)" % (data, attrs.get(key))
            res.append((key, data))
        return res

    def get_prod_by_location(self, cr, uid, loc_id, product_ids=False, context={}, states=['done'], what=('in', 'out')):
        product_obj = self.pool.get('product.product')
        context.update({
            'states': states,
            'what': what,
            'location': loc_id
        })
        results = product_obj.get_product_available(cr, uid, product_ids, context=context)
        return dict((str(key), value) for key, value in results.items())

    def _get_stock_moves(self, cr, uid, ids, field_name, arg, context=None):
        res = {}.fromkeys(ids, {'stock_move_ids':[], 'dimension_ids':[]})
        if not ids:
            return res

        #raws = comm.is_raw_material_by_product_id(self, cr, uid, ids)
        raws = { rec.id : (rec.prod_type == comm.RAW) for rec in self.pool.get('product.template').browse(cr, uid, ids)}
        _logger.info(">> _get_stock_moves >> 3 >> raws = %s", raws)

        for pid in ids:
            if not raws[pid]:
                continue

            sql = "SELECT id, dimension_id FROM stock_move"\
                  " WHERE product_id = %s ORDER BY date DESC" % (pid,)

            cr.execute(sql)
            for r in cr.fetchall():
                if r and r[0] and (not r[0] in res[pid]['stock_move_ids']):
                    res[pid]['stock_move_ids'].append(r[0])

                if r and r[1] and (not r[1] in res[pid]['dimension_ids']):
                    res[pid]['dimension_ids'].append(r[1])

            if res[pid]['dimension_ids']:
                dim_obj = self.pool.get('product.marble.dimension.balance')
                dim_ids = dim_obj.search(cr, uid, [('product_id','=',pid)])

                res[pid]['dimension_total_m2'] = 0.000
                for d in dim_obj.browse(cr, uid, dim_ids, context):
                    res[pid]['dimension_total_m2'] += d.qty_m2

        # _logger.info(">> _get_stock_moves >> 4 >> res = %s", res)
        return res

    #def _is_raw(self, cr, uid, ids, field_name, arg, context=None):
    #    res = { sm.id : (sm.product_id.prod_type == comm.RAW) for sm in self.browse(cr, uid, ids) }
    #    _logger.info("10 >> _is_raw >> res = %s", res)
    #    return res

    _columns = {
        'raw_material': fields.selection(_get_material, string='Category'),
        'raw_color': fields.selection(_get_color, string='Color'),
        'raw_finished': fields.selection(_get_finished, string='Finished'),
        'movile_categ_name': fields.char('flag', size=100, required=False, store=False),

        'bacha_material': fields.selection(_get_bacha_material, string='Material'),
        'bacha_marca': fields.selection(_get_bacha_marca, string='Marca'),
        'bacha_acero': fields.selection(_get_bacha_acero, string='Acero'),
        'bacha_colocacion': fields.selection(_get_bacha_colocacion, string='Colocacion'),
        'bacha_tipo': fields.selection(_get_bacha_tipo, string='Tipo'),
        'bacha_ancho': fields.float('Ancho', digits=(5, 2), type="float"),
        'bacha_largo': fields.float('Largo', digits=(5, 2), type="float"),
        'bacha_prof': fields.float('Profundidad', digits=(5, 2), type="float"),
        'bacha_diam': fields.float('Diametro', digits=(5, 2), type="float"),

#        'categ_name': fields.related('categ_id', 'name', relation='product.category', type='char', readonly=True, string='Category'),
        'prod_type': fields.related('categ_id', 'prod_type', relation='product.category', type='char', readonly=True, string='Prod Type', store=True),

#        'is_raw': fields.function(_is_raw_material, type='boolean', string='Is Raw Material'),
#        'is_bacha': fields.function(_is_bacha, type='boolean', string='Is Bacha'),
#        'is_input': fields.function(_is_input, type='boolean', string='Is Insumo'),

#        'uom_readonly': fields.function(_get_uom_readonly, type='boolean', string='Is Raw or Bacha'),
        'attrs_material': fields.function(_attrs_material, type='char', string='Details'),

        'dimension_ids': fields.function(_get_stock_moves, relation='product.marble.dimension', type="one2many", string='Dimensions', multi="*"),
        'stock_move_ids': fields.function(_get_stock_moves, relation='stock.move', type="one2many", string='Stock Moves', multi="*"),
        'dimension_total_m2': fields.function(_get_stock_moves, type="float", digits=(5,2), string='Area Total [m2]', multi="*"),
    }

product_template()


#class product_product(osv.osv):
#    _name = 'product.product'
#    _inherit = 'product.product'
#
#    def _get_stock_moves(self, cr, uid, ids, field_name, arg, context=None):
#        res = {}.fromkeys(ids, {'stock_move_ids':[], 'dimension_ids':[]})
#        if not ids:
#            return res
#
#        raws = comm.is_raw_material_by_product_id(self, cr, uid, ids)
#        for pid in ids:
#            if not raws[pid]:
#                continue
#
#            sql = "SELECT id, dimension_id FROM stock_move"\
#                  " WHERE product_id = %s ORDER BY date DESC" % (pid,)
#
#            cr.execute(sql)
#            for r in cr.fetchall():
#                if r and r[0] and (not r[0] in res[pid]['stock_move_ids']):
#                    res[pid]['stock_move_ids'].append(r[0])
#
#                if r and r[1] and (not r[1] in res[pid]['dimension_ids']):
#                    res[pid]['dimension_ids'].append(r[1])
#
#            if res[pid]['dimension_ids']:
#                dim_obj = self.pool.get('product.marble.dimension.balance')
#                dim_ids = dim_obj.search(cr, uid, [('product_id','=',pid)])
#
#                res[pid]['dimension_total_m2'] = 0.000
#                for d in dim_obj.browse(cr, uid, dim_ids, context):
#                    res[pid]['dimension_total_m2'] += d.qty_m2
#
#        # _logger.info(">> _get_stock_moves >> 4 >> res = %s", res)
#        return res
#
#    _columns = {
#        'dimension_ids': fields.function(_get_stock_moves, relation='product.marble.dimension', type="one2many", string='Dimensions', multi="*"),
#        'stock_move_ids': fields.function(_get_stock_moves, relation='stock.move', type="one2many", string='Stock Moves', multi="*"),
#        'dimension_total_m2': fields.function(_get_stock_moves, type="float", digits=(5,2), string='Area Total [m2]', multi="*"),
#    }
#
#product_product()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
