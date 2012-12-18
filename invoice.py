# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (C) 2012 OpenERP - Team de Localización Argentina.
# https://launchpad.net/~openerp-l10n-ar-localization
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from osv import fields, osv
from tools.translate import _
import decimal_precision as dp

_all_taxes = lambda x: True
_all_except_vat = lambda x: x.name not in [u'IVA Ventas 21%', u'IVA Compras 21%']

class account_invoice_line(osv.osv):
    """
    En argentina como no se diferencian los impuestos en las facturas, excepto el IVA
    agrego funciones que ignoran el iva solamenta a la hora de imprimir los valores.
    """
    def _amount_calc_taxes(self, cr, uid, ids, tax_filter, default_quantity):
        res = {}
        tax_obj = self.pool.get('account.tax')
        cur_obj = self.pool.get('res.currency')
        for line in self.browse(cr, uid, ids):
            price = line.price_unit * (1-(line.discount or 0.0)/100.0)
            tax_ids = filter(tax_filter, line.invoice_line_tax_id)
            quantity = default_quantity if default_quantity is not None else line.quantity
            taxes = tax_obj.compute_all(cr, uid,
                                        tax_ids, price, quantity,
                                        product=line.product_id,
                                        address_id=line.invoice_id.address_invoice_id,
                                        partner=line.invoice_id.partner_id)
            res[line.id] = taxes['total_included']
            if line.invoice_id:
                cur = line.invoice_id.currency_id
                res[line.id] = cur_obj.round(cr, uid, cur, res[line.id])
        return res

    def _amount_unit_vat_included(self, cr, uid, ids, prop, unknow_none, unknow_dict):
        return self._amount_calc_taxes(cr, uid, ids, _all_taxes, 1)

    def _amount_subtotal_vat_included(self, cr, uid, ids, prop, unknow_none, unknow_dict):
        return self._amount_calc_taxes(cr, uid, ids, _all_taxes, None)

    def _amount_unit_not_vat_included(self, cr, uid, ids, prop, unknow_none, unknow_dict):
        return self._amount_calc_taxes(cr, uid, ids, _all_except_vat, 1)

    def _amount_subtotal_not_vat_included(self, cr, uid, ids, prop, unknow_none, unknow_dict):
        return self._amount_calc_taxes(cr, uid, ids, _all_except_vat, None)

    _inherit = "account.invoice.line"
    _columns = {
        'price_unit_vat_included': fields.function(_amount_unit_vat_included, method=True,
                                               string='Unit Price with VAT', type="float",
                                               digits_compute= dp.get_precision('Account'), store=False),
        'price_subtotal_vat_included': fields.function(_amount_subtotal_vat_included, method=True,
                                               string='Subtotal with VAT', type="float",
                                               digits_compute= dp.get_precision('Account'), store=False),
        'price_unit_not_vat_included': fields.function(_amount_unit_not_vat_included, method=True,
                                               string='Unit Price without VAT', type="float",
                                               digits_compute= dp.get_precision('Account'), store=False),
        'price_subtotal_not_vat_included': fields.function(_amount_subtotal_not_vat_included, method=True,
                                               string='Subtotal without VAT', type="float",
                                               digits_compute= dp.get_precision('Account'), store=False),
    }
account_invoice_line()

class account_invoice(osv.osv):
    _inherit = "account.invoice"

    def action_date_assign(self, cr, uid, ids, context={}):
        r = self.afip_validation(cr, uid, ids, context)
        r = r and super(account_invoice, self).action_date_assign(cr, uid, ids, context)
        return r

    def afip_validation(self, cr, uid, ids, context={}):
        obj_resp_class = self.pool.get('afip.responsability_class')

        for invoice in self.browse(cr, uid, ids):
            # Partner responsability ?
            if isinstance(invoice.partner_id.responsability_id, osv.orm.browse_null):
                raise osv.except_osv(_('No responsability'),
                                     _('Your partner have not afip responsability assigned. Assign one please.'))

            # Take responsability classes for this journal
            invoice_class = invoice.journal_id.journal_class_id.document_class
            resp_class_ids = obj_resp_class.search(cr, uid, [('document_class','=', invoice_class)])

            # You can emmit this document?
            resp_class = [ rc.emisor_id.code for rc in obj_resp_class.browse(cr, uid, resp_class_ids) ]
            if invoice.journal_id.company_id.partner_id.responsability_id.code not in resp_class:
                import pdb; pdb.set_trace()
                raise osv.except_osv(_('Invalid emisor'),
                                     _('Your responsability with AFIP dont let you generate this kind of document.'))

            # Partner can receive this document?
            resp_class = [ rc.receptor_id.code for rc in obj_resp_class.browse(cr, uid, resp_class_ids) ]
            if invoice.partner_id.responsability_id.code not in resp_class:
                raise osv.except_osv(_('Invalid receptor'),
                                     _('Your partner cant recive this document. Check AFIP responsability of the partner, or Journal Account of the invoice.'))

            # If Final Consumer have pay more than 1000$, you need more information to generate document.
            if invoice.partner_id.responsability_id.code == 'CF' and invoice.amount_total > 1000 and \
               (invoice.partner_id.document_type.code in [ None, 'Sigd' ] or invoice.partner_id.document_number is None):
                raise osv.except_osv(_('Partner without Identification for total invoices > $1000.-'),
                                     _('You must define valid document type and number for this Final Consumer.'))
        return True

account_invoice()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

