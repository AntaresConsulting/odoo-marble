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
from openerp import api, exceptions
from openerp.osv import fields, osv

import logging
_logger = logging.getLogger(__name__)

class res_partner(osv.osv):
    _inherit = 'res.partner'

    _columns = {
        'website': fields.char('Website', size=64, help="Website of Partner or Company", select=True),
        'has_works': fields.boolean('Has works', help="Check this box if this contact has works."),
        'is_work': fields.boolean('Is a Work', help="This contact is a work."),
        'child_ids': fields.one2many('res.partner', 'parent_id', 'Contacts', domain=[('active','=',True),('is_work','=',False)]), # force "active_test" domain to bypass _search() override
        'works_ids': fields.one2many('res.partner', 'parent_id', 'Works', domain=[('active','=',True),('is_work','=',True)]), # force "active_test" domain to bypass _search() override
    }

    _defaults = {
        'has_works' : False,
        'is_work'   : api.model(lambda self: self.env.context.get('is_work',False)),
        'works_ids' : [],
    }

    @api.onchange('is_company')
    def _onchange_is_company(self):
        if not self.is_company and len(self.works_ids):
            self.is_company = True
            return { 'warning': {
                        'title': 'Waring',
                        'message': 'This Partner has Works assigned so you do not disable "Company".',
            } }
        return super(res_partner,self).onchange_type(self.is_company)

    @api.onchange('customer','has_works')
    def _onchange_customer(self):
        if not (self.customer and self.has_works) and len(self.works_ids):
            self.customer = True
            self.has_work = True
            return { 'warning': {
                        'title': 'Waring',
                        'message': 'This Partner has Works assigned so you do not disable "Customer" or "Has Work".',
            } }

res_partner()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
