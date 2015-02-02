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

from openerp import models, fields, api
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from datetime import datetime

import logging
_logger = logging.getLogger(__name__)

class stock_transfer_details(models.TransientModel):
    _name = 'stock.transfer_details'
    _inherit = 'stock.transfer_details'
    _description = 'Picking wizard'

    #dimension_id = fields.Many2one('product.marble.dimension', 'Dimension', doman=[('state','=','done')])
    #dimension_unit = fields.Integer(string='Units')
    #prod_type = fields.Char(related='product_id.prod_type', string='Product Type')

#    def default_get(self, cr, uid, fields, context):
#        res = super(stock_transfer_details, self).default_get(cr, uid, fields, context=context)
#        _logger.info('>> default_get >> 1- res = %s', res)
#        _logger.info('>> default_get >> 2- fields = %s', fields)
#        _logger.info('>> default_get >> 3- context = %s', context)
#
#        _logger.info('>> default_get >> 4- items = %s', res.get('item_ids',False))
#        _logger.info('>> default_get >> 5- items = %s', res.get('packop_ids',False))
#
#        obj_prod = self.pool.get('product.product')
#        items = []
#        for item in res.get('item_ids', False):
#            _logger.info('>> default_get >> 6- item = %s', item)
#            prod = obj_prod.browse(cr,uid,item.product_id,context=context)
#
#       return res
#
#        packop_ids = res.get('packop_ids',False)
#
#        _logger.info('>> default_get >> 4- item_ids = %s', item_ids)
#        _logger.info('>> default_get >> 5- packop_ids = %s', packop_ids)
#
#        for pick_id in self.pool.get('stock.picking').browse(cr, uid, ids, context):
#            #dimension_id = pick_id.move_lines.search([('product_id','=',pick_id.product_id.id)])[0].dimension_id
#            #dimension_unit =
#            _logger.info('>> default_get >> 7- pick_id = %s', pick_id)
#
#            mov = pick_id.move_lines.search([('product_id','=',pick_id.product_id.id)])
#            _logger.info('>> default_get >> 8- mov = %s', mov)
#
#        _logger.info('>> default_get >> 9- res = %s', res)
#        return res
#
#stock_transfer_details()

class stock_transfer_details_items(models.TransientModel):
    _name = 'stock.transfer_details_items'
    _inherit = 'stock.transfer_details_items'
    _description = 'Picking wizard items'

    dimension_id = fields.Many2one('product.marble.dimension', 'Dimension', doman=[('state','=','done')])
    dimension_unit = fields.Integer(string='Units')
    prod_type = fields.Char(related='product_id.prod_type', string='Product Type')

#    def default_get(self, cr, uid, fields, context):
#        res = super(stock_transfer_details_items, self).default_get(cr, uid, fields, context=context)
#        _logger.info('>> default_get >> 1- res = %s', res)
#        _logger.info('>> default_get >> 2- fields = %s', fields)
#        _logger.info('>> default_get >> 3- context = %s', context)
#        #for tra in self.pool.get('stock.transfer_details_items').browse(cr, uid, )
#        return res

stock_transfer_details_items()

