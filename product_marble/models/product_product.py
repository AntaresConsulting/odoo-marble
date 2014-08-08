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

from openerp.osv import osv
from openerp.osv import fields
from openerp.tools.translate import _
from operator import itemgetter

# import pdb

import _common as comm
import logging

_logger = logging.getLogger(__name__)

class product_product(osv.osv):
    _inherit = 'product.product'

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
    
    def _get_material(self, cr, uid, context=None):
        return sorted(self._material, key=itemgetter(1))

    def _get_color(self, cr, uid, context=None):
        return sorted(self._color, key=itemgetter(1))

    def _get_finished(self, cr, uid, context=None):
        return sorted(self._finished, key=itemgetter(1))

    def _get_bacha_tipo(self, cr, uid, context=None):
        return sorted(self._bacha_tipo, key=itemgetter(1))

    def _get_bacha_colocacion(self, cr, uid, context=None):
        return sorted(self._bacha_colocacion, key=itemgetter(1))

    def _get_bacha_acero(self, cr, uid, context=None):
        return sorted(self._bacha_acero, key=itemgetter(1))

    def _get_bacha_material(self, cr, uid, context=None):
        return sorted(self._bacha_material, key=itemgetter(1))

    def _get_bacha_marca(self, cr, uid, context=None):
        return sorted(self._bacha_marca, key=itemgetter(1))

    def _get_stock_moves(self, cr, uid, ids, field_name, arg, context=None):
        res = {}.fromkeys(ids, {'stock_move_ids':[], 'dimension_ids':[]})

        # _logger.info(">> _get_stock_moves >> 1 >> res = %s", res)
        # _logger.info(">> _get_stock_moves >> 1b >> context = %s", context)
        if not ids:
            return res

        raws = comm.is_raw_material_by_product_id(self, cr, uid, ids)
        for pid in ids:
            if not raws[pid]:
                continue

            sql = "SELECT id, dimension_id FROM stock_move"\
                  " WHERE product_id = %s ORDER BY date" % (pid,)

            # _logger.info(">> _get_stock_moves >> 2 >> sql = %s", sql)

            cr.execute(sql)
            for r in cr.fetchall():
                # _logger.info(">> _get_stock_moves >> 3 >> r = %s", r)

                if r and r[0] and (not r[0] in res[pid]['stock_move_ids']):
                    res[pid]['stock_move_ids'].append(r[0])

                if r and r[1] and (not r[1] in res[pid]['dimension_ids']):
                    res[pid]['dimension_ids'].append(r[1])

        # _logger.info(">> _get_stock_moves >> 4 >> res = %s", res)
        return res

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


    def _is_raw_material(self, cr, uid, ids, field_name, arg, context=None):
        """
        Determina si [ids products] es de la categoria "Marble Work" si/no...
        return: {id: False/True, ..}
        """
        return comm.is_raw_material_by_product_id(self, cr, uid, ids)


    def _is_bacha(self, cr, uid, ids, field_name, arg, context=None):
        return comm.is_bacha_by_product_id(self, cr, uid, ids)


    def _get_categ_raw_material_id(self, cr, uid, ids, field_name, arg, context=None):
        cid = comm.get_raw_material_id(self, cr, uid)
        res = {}.fromkeys(ids,[cid])

        # _logger.info(">> _get_categ_raw_material_id >> 88 >> res = %s", res)
        return res


    def _get_categ_marble_domain(self, cr, uid, ids, field_name, arg, context=None):
        """
        Define: Filter Domain para determinar Category Marble
        return: {'id': '[1,2,3, ..]'}
        """
        res = {}
        if not ids:
            return res

        cid = comm.get_raw_material_id(self, cr, uid)
        res = {}.fromkeys(ids,[cid])

        # _logger.info(">> _get_categ_marble_domain >> 2 >> res = %s", res)
        return res


    def onchange_category_id(self, cr, uid, ids, categ_id):
        """
        Se cambio Categ. Prod, >> determino y seteo la view segun Categ. Prod.
        """
        v = {}
        if not categ_id:
            return v

        v['is_raw'] = False
        v['is_bacha'] = False
        v['uom_readonly'] = False

        if comm.is_raw_material(self, cr, uid, categ_id):
            v['type'] = 'product'
            v['is_raw'] = True
            v['uom_readonly'] = True
            v['uom_id'] = comm.get_uom_m2_id(self, cr, uid)
            v['uom_po_id'] = comm.get_uom_m2_id(self, cr, uid)

        elif comm.is_bachas(self, cr, uid, categ_id):
            v['type'] = 'product'
            v['is_bacha'] = True
            v['uom_readonly'] = True
            v['uom_id'] = comm.get_uom_units_id(self, cr, uid)
            v['uom_po_id'] = comm.get_uom_units_id(self, cr, uid)

        elif comm.is_inputs(self, cr, uid, categ_id):
            v['type'] = 'consu'

        elif comm.is_services(self, cr, uid, categ_id):
            v['type'] = 'service'

        # _logger.info("10 >> onchange_category_id >> v = %s", v)
        return {'value': v}


    def _check_data_before_save(self, cr, uid, data):
        # import pdb
        # pdb.set_trace()
        # _logger.info(">> check_before >> 1 >> data = %s", data)

        if 'categ_id' in data:
            cid = data['categ_id']
            # if not comm.is_raw_material_by_category_id(self, cr, uid, [cid])[cid]:
            if comm.is_raw_material(self, cr, uid, cid):
                data['type'] = 'product'
                data['uom_id'] = comm.get_uom_m2_id(self, cr, uid)
                data['uom_po_id'] = comm.get_uom_m2_id(self, cr, uid)
                data['bacha_material'] = False
                data['bacha_marca'] = False

            elif comm.is_bachas(self, cr, uid, cid):
                data['type'] = 'product'
                data['uom_id'] = comm.get_uom_units_id(self, cr, uid)
                data['uom_po_id'] = comm.get_uom_units_id(self, cr, uid)
                data['material'] = False
                data['color'] = False
                data['finished'] = False

            else:
                if comm.is_inputs(self, cr, uid, cid):
                    data['type'] = 'consu'
                elif comm.is_services(self, cr, uid, cid):
                    data['type'] = 'service'

#                data['material'] = False
#                data['color'] = False
#                data['finished'] = False
#                data['bacha_material'] = False
#                data['bacha_marca'] = False

        # _logger.info(">> check_before >> 2 >> data = %s", data)

    def create(self, cr, uid, data, context=None):
        if 'categ_id' in data:
            self._check_data_before_save(cr, uid, data)

        # _logger.info(">> create >> 2 >> data = %s", data)
        return super(product_product, self).create(cr, uid, data, context=context)


    def write(self, cr, uid, ids, vals, context=None):
        if 'categ_id' in vals:
            self._check_data_before_save(cr, uid, vals)

        # _logger.info(">> write >> 3 >> vals = %s", vals)
        return super(product_product, self).write(cr, uid, ids, vals, context=context)


    def _get_attrs(self, cr, uid, ids, context=None):
        res = {}
        if not ids:
            return res

        for p in self.browse(cr, uid, ids, context=context):

            attrs = ""
            if comm.is_raw_material(self, cr, uid, p.categ_id.id):
                mat = dict(self._material).get(p.material)
                col = dict(self._color).get(p.color)
                fin = dict(self._finished).get(p.finished)
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
        names = super(product_product, self).name_get(cr, uid, ids, context=context)
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

    def name_search(self, cr, uid, name='', args=None, operator='ilike', context=None, limit=10):
        ids = []
        ids = self.search(cr, uid, ids, context=context)
        return self.name_get(cr, uid, ids, context=context)


    def _search_marble(self, cr, uid, obj=None, name=None, args=None, context=None):
        return [('is_raw_material','=',True)]

    _columns = {
        'material': fields.selection(_get_material, string='Category', select=True),
        'color': fields.selection(_get_color, string='Color', select=True),
        'finished': fields.selection(_get_finished, string='Finished', select=True),

        'bacha_material': fields.selection(_get_bacha_material, string='Material', select=True),
        'bacha_marca': fields.selection(_get_bacha_marca, string='Marca', select=True),
        'bacha_acero': fields.selection(_get_bacha_acero, string='Acero', select=True),
        'bacha_colocacion': fields.selection(_get_bacha_colocacion, string='Colocaicon', select=True),
        'bacha_tipo': fields.selection(_get_bacha_tipo, string='Tipo', select=True),
        'bacha_ancho': fields.float('Bacha Ancho', digits=(5, 2), type="float"),
        'bacha_largo': fields.float('Bacha Largo', digits=(5, 2), type="float"),
        'bacha_prof': fields.float('Bacha Profundidad', digits=(5, 2), type="float"),
        'bacha_diam': fields.float('Bacha Profundidad', digits=(5, 2), type="float"),
        
        
        'categ_name': fields.related('categ_id', 'name', relation='product.category', type='char', readonly=True, string='Category'),
        'is_raw': fields.function(_is_raw_material, type='boolean', string='Is Raw Material'),
        'is_bacha': fields.function(_is_bacha, type='boolean', string='Is Bacha'),
        'uom_readonly': fields.function(_get_uom_readonly, type='boolean', string='Is Raw or Bacha'),
        'attrs_material': fields.function(_attrs_material, type='char', string='Details'),

        'dimension_ids': fields.function(_get_stock_moves, relation='product.marble.dimension', type="one2many", string='Dimensions', multi="*"),
        'stock_move_ids': fields.function(_get_stock_moves, relation='stock.move', type="one2many", string='Stock Moves', multi="*"),
    }

product_product()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
