# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-TODAY OpenERP S.A. <http://www.odoo.com>
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

from openerp import models, fields, api, exceptions
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from datetime import datetime
import _common as comm

import logging
_logger = logging.getLogger(__name__)

class stock_transfer_details(models.TransientModel):
    _name = 'stock.transfer_details'
    _inherit = 'stock.transfer_details'
    _description = 'Picking wizard'

    def default_get(self, cr, uid, fields, context):
        res = super(stock_transfer_details, self).default_get(cr, uid, fields, context=context)
        #_logger.info('>> default_get >> 4- res = %s', res)
        items = res.get('item_ids',False)
        packs = res.get('packop_ids',False)
        obj_opera = self.pool.get('stock.pack.operation')
        for elem in items + packs:
            #_logger.info('>> default_get >> 5- elem = %s', elem)
            opera = obj_opera.browse(cr, uid, elem.get('packop_id',False))
            elem.update(dimension_id = opera.dimension_id.id)
            elem.update(dimension_unit = opera.dimension_unit)
        #_logger.info('>> default_get >> 6- res = %s', res)
        return res

    @api.one
    def do_detailed_transfer(self):
        processed_ids = []
        # Create new and update existing pack operations
        for lstits in [self.item_ids, self.packop_ids]:
            for prod in lstits:
                _logger.info('>> do_detailed_transfer >> 0- prod = %s', prod)
                _logger.info('>> do_detailed_transfer >> 1- prod = %s', prod.product_id.id)
                _logger.info('>> do_detailed_transfer >> 2- dim = %s',  prod.dimension_id.id)
                _logger.info('>> do_detailed_transfer >> 3- unit = %s', prod.dimension_unit)
                _logger.info('>> do_detailed_transfer >> 4- qty = %s',  prod.quantity)
                #return False
                pack_datas = {
                    'product_id':        prod.product_id.id,
                    'product_uom_id':    prod.product_uom_id.id,
                    'product_qty':       prod.quantity,
                    'package_id':        prod.package_id.id,
                    'lot_id':            prod.lot_id.id,
                    'location_id':       prod.sourceloc_id.id,
                    'location_dest_id':  prod.destinationloc_id.id,
                    'result_package_id': prod.result_package_id.id,
                    'date':              prod.date if prod.date else datetime.now(),
                    'owner_id':          prod.owner_id.id,
                    # add by marble...
                    'dimension_id':      prod.dimension_id.id,
                    'dimension_unit':    prod.dimension_unit,
                }
                if prod.packop_id:
                    prod.packop_id.write(pack_datas)
                    processed_ids.append(prod.packop_id.id)
                else:
                    pack_datas['picking_id'] = self.picking_id.id
                    packop_id = self.env['stock.pack.operation'].create(pack_datas)
                    processed_ids.append(packop_id.id)
        # Delete the others
        packops = self.env['stock.pack.operation'].search(['&', ('picking_id', '=', self.picking_id.id), '!', ('id', 'in', processed_ids)])
        for packop in packops:
            packop.unlink()
        # Execute the transfer of the picking
        self.picking_id.do_transfer()
        return True

stock_transfer_details()


class stock_transfer_details_items(models.TransientModel):
    _name = 'stock.transfer_details_items'
    _inherit = 'stock.transfer_details_items'
    _description = 'Picking wizard items'

    prod_type = fields.Char(related='product_id.prod_type', string='Product Type')
    dimension_id = fields.Many2one('product.marble.dimension', 'Dimension', domain=[('state','=','done')])
    dimension_unit = fields.Integer(string='Units')

    @api.multi
    def calculate_dim(self):
        if not (self.product_id and self.product_id.id): return
        if self.product_id.prod_type == comm.RAW:
            m2 = self.dimension_id.m2 if self.dimension_id else 0.00
            self.quantity = (m2 * self.dimension_unit)
            #_logger.info('>> calculate_dim >> 2- %sm2 x %sunit = %sqty', m2, self.dimension_unit, self.quantity)
        else:
            self.dimension_id = False
            self.dimension_unit = 0

    @api.onchange('product_id')
    def product_id_change(self):
        res = super(stock_transfer_details_items, self).product_id_change(self.product_id.id, self.product_uom_id.id)

        # v7 > v8 # paso 'value' a 'self'
        uom = res.get('value', False) and res['value'].get('product_uom_id', False)
        if uom: self.product_uom_id = uom

        self.calculate_dim()
        #_logger.info('>> product_id_change >> 2- self = %s', self)

    @api.onchange('dimension_id', 'dimension_unit')
    def dimension_change(self):
        self.calculate_dim()
        #_logger.info('>> product_id_change >> 2- self = %s', self)

    @api.multi
    def write(self, vals, context=None):
        _logger.info('>> item.write >> 3- vals = %s',  vals)

        prod_id     = vals.get('product_id',    self.product_id.id)
        dim_id      = vals.get('dimension_id',  self.dimension_id.id)
        dim_unit    = vals.get('dimension_unit',self.dimension_unit)
        qty         = vals.get('quantity',      self.quantity)

        prod = self.env['product.product'].browse(prod_id)
        if prod.prod_type == comm.RAW:
            if not dim_id:   raise exceptions.ValidationError("Debe seleccionar 'Dimension'.")
            if not dim_unit: raise exceptions.ValidationError("Debe indicar 'Unit'.")
            m2 = self.env['product.marble.dimension'].browse(dim_id).m2
            vals.update(quantity = (m2 * dim_unit))
        else:
            vals.update(dimension_id = False, dimension_unit = 0)

        _logger.info('>> item.write >> 4- vals = %s', vals)
        return super(stock_transfer_details_items, self).write(vals)

stock_transfer_details_items()

