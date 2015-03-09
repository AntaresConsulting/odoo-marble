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

from openerp import models, api, registry, _
from openerp.osv import osv
from openerp.osv import fields
# from openerp.tools.translate import _
from operator import itemgetter

import logging
_logger = logging.getLogger(__name__)

# import pdb
# pdb.set_trace()

class product_marble_dimension(osv.osv):
    _name = 'product.marble.dimension'
    _description = "Dimension"

    @api.model
    def _get_type(self):
        return sorted((('pla', _("Plaque")),('lef', _("Leftover")),('mar', _("Marmeta"))), key=itemgetter(1))

# --- Migracion -------------------------
#
    def _compute_totals(self, cr, uid, ids, field_name, arg, context=None):
        # _logger.info(">> _compute_totals >> 1 >> ids = %s", ids)

        res = {}.fromkeys(ids, {'total_units':0, 'total_m2':0.000})
        if not ids:
            return res

        pid = context.get('product_id') if context else 0

        obj = self.pool.get('product.marble.dimension.balance')
        bids = obj.search(cr, uid, [('product_id','=',pid),('dimension_id','in', ids)], context=context)
        data = obj.browse(cr, uid, bids)

        # _logger.info(">> _compute_totals >> 2 >> bds = %s", bids)
        # _logger.info(">> _compute_totals >> 3 >> data = %s", data)
        for d in data:
            res[d.dimension_id.id] = {'total_units': d.qty_unit, 'total_m2': d.qty_m2}

        # _logger.info(">> _compute_totals >> 4 >> res = %s", res)
        return res

#    @api.multi
#    def _compute_totals(self, field_name):
#        _logger.info(">> _compute_totals >> 1 >> ids = %s", self.ids)
#
#        if len(self) == 0:
#            return
#
#        ids = self.ids
#        pid = self._context.get('product_id') if self._context else 0
#
#        model = registry['product.marble.dimension.balance']
#        assert isinstance(model, Model)
#
#        data = model.search([('product_id','=',pid),('dimension_id','in', ids)])
#        for d in data:
#
#        # -------------------------------
#
#        res = {}.fromkeys(ids, {'total_units':0, 'total_m2':0.000})
#        if not ids:
#            return res
#
#        pid = context.get('product_id') if context else 0
#
#        obj = self.pool.get('product.marble.dimension.balance')
#        bids = obj.search(cr, uid, [('product_id','=',pid),('dimension_id','in', ids)], context=context)
#        data = obj.browse(cr, uid, bids)
#
#        _logger.info(">> _compute_totals >> 2 >> bds = %s", bids)
#        _logger.info(">> _compute_totals >> 3 >> data = %s", data)
#        for d in data:
#            res[d.dimension_id.id] = {'total_units': d.qty_unit, 'total_m2': d.qty_m2}
#
#        _logger.info(">> _compute_totals >> 4 >> res = %s", res)
#        return res


#        sql = "SELECT dimension_id, SUM(dimension_unit), SUM(product_qty) FROM stock_move" \
#              " WHERE dimension_id IS NOT NULL AND product_id = %s GROUP BY dimension_id" % (pid)
#        # _logger.info(">> _compute_totals >> 4 >> sql = %s", sql)

#        cr.execute(sql)
#        data = cr.fetchall()

#        # _logger.info(">> _compute_totals >> 5 >> data = %s", data)
#        for r in data:
#            if r:
#                res[r[0]] = {'total_units': r[1], 'total_m2': r[2]}

#        # _logger.info(">> _compute_totals >> 7 >> res = %s", res)
#        return res


#    def _calculate_m2(self, cr, uid, ids, field_name, arg, context=None):
#        res = {}
#        res = {p.id:(p.hight * p.width) for p in self.browse(cr, uid, ids, context=context)}
#        return res

    def surface_get(self, cr, uid, ids, context=None):
        """
        Retorna >> (hight m x width m) >> (9.99 m x 9.99 m)
        return: {dimensions_id: str, ...}
        """
        result = {}
        if not all(ids):
            return result

        for p in self.browse(cr, uid, ids, context=context):
            dimension = "(%5.2fm x %5.2fm)" % (p.hight, p.width)
            result.update({p.id: dimension})

        return result

#    def name_get(self, cr, uid, ids, context=None):
#        result = []
#        if not all(ids):
#            return result
#
#        for p in self.browse(cr, uid, ids, context=context):
#            dimension = "(%5.2f m x %5.2f m) = %5.2f m2" % (p.hight, p.width, p.m2)
#            result.append((p.id, dimension))
#
#        return result

#    def name_search(self, cr, uid, name='', args=None, operator='ilike', context=None, limit=10):
#        ids = self.search(cr, uid, [], context=context)
#        return self.name_get(cr, uid, ids, context=context)

#    def _get_dimension(self, cr, uid, ids, field_name, arg, context=None):
#        res = self.name_get(cr, uid, ids, context=context)
#        _logger.info(">> _get_dimension >> 1 >> res = %s", res)
#
#        res = dict(res)
#        _logger.info(">> _get_dimension >> 2 >> res = %s", res)
#
#        return res

    def _get_dimension(self, ty, hi, wi, th, m2):
        ty_dim = dict((('pla', _("Plaque")),('lef', _("Leftover")),('mar', _("Marmeta")))).get(ty, '<N/I>')
        dim = "%s: [%5.2fm](%5.2fm x %5.2fm) = %5.2fm2" % (ty_dim, th, hi, wi, m2)
        # _logger.info(">> _get_dimension >> 3 >> dim = %s", dim)
        return dim

    def _get_m2(self, hi, wi, th):
        v = {}
        v['hight'] = hi if hi else 0.000
        v['width'] = wi if wi else 0.000
        v['thickness'] = th if th else 0.000
        v['m2'] = v['hight'] * v['width']
        return v

    def onchange_calculate_m2(self, cr, uid, ids, ty, hi, wi, th, context=None):
        v = self._get_m2(hi, wi, th)
        v['dimension'] = self._get_dimension(ty, v['hight'], v['width'], v['thickness'], v['m2'])
        return {'value':v}

    def action_confirm(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'done'})
        return True

    def _check_data_before_save(self, cr, uid, ids, data, is_new=False):
        # _logger.info(">> _check_data_before_save >> 1 >> data = %s", data)
        if is_new:
            hi = data.get('hight',0.000)
            wi = data.get('width',0.000)
            th = data.get('thickness',0.000)
            ty = data.get('type','<N/I>')
        else:
            dim = self.browse(cr, uid, ids, context=None)[0]
            hi = data.get('hight',0.000) if ('hight' in data) else dim.hight
            wi = data.get('width',0.000) if ('width' in data) else dim.width
            th = data.get('thickness',0.000) if ('thickness' in data) else dim.thickness
            ty = data.get('type','<N/I>') if ('type' in data) else dim.type

        data['m2'] = float(hi) * float(wi)
        data['dimension'] = self._get_dimension(ty, float(hi), float(wi), float(th), (float(hi)*float(wi)))
        # _logger.info(">> _check_data_before_save >> 2 >> data = %s", data)

    def create(self, cr, uid, data, context=None):
        self._check_data_before_save(cr, uid, [], data, True)
        return super(product_marble_dimension, self).create(cr, uid, data, context=context)

    def write(self, cr, uid, ids, vals, context=None):
        self._check_data_before_save(cr, uid, ids, vals, False)
        return super(product_marble_dimension, self).write(cr, uid, ids, vals, context=context)

    _columns = {
        'hight': fields.float('Hight', digits=(5, 3), required=True, states={'done':[('readonly', True)]}),
        'width': fields.float('Width', digits=(5, 3), required=True, states={'done':[('readonly', True)]}),
        'm2': fields.float('Area (m2)', digits=(5, 3), required=True, readonly=True),

        'dimension': fields.char('Dimension', type='char', size=50),
        'thickness': fields.float('Thickness', digits=(5, 3), required=True, states={'done':[('readonly', True)]}),
        'type': fields.selection(_get_type, string='Type', required=False, states={'done':[('readonly', True)]}),

        'state': fields.selection([('draft', 'Draft'),('done', 'Dimensioned')],'Status', readonly=True),

        'total_units': fields.function(_compute_totals, string='Units', type='integer', multi='compute_totals'),
        'total_m2': fields.function(_compute_totals, string='Area [m2]', type='float', multi='compute_totals'),
    }

    _defaults = {
        'hight': lambda *a: 0.000,
        'width': lambda *a: 0.000,
        'thickness': lambda *a: 0.000,
        'm2': lambda *a: 0.000,
        'dimension': lambda self, cr, uid: self._get_dimension('pla', 0.000, 0.000, 0.000),
        'type': 'pla',
        'state': 'draft'
    }

    _rec_name = 'dimension'

product_marble_dimension()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
